/// <reference types="@figma/plugin-typings" />

// Thin adapter -- executes a FigmaRenderPlan built in Python
// (integrations/figma/render_plan/compiler.py). No design interpretation
// happens here: every operation below maps to exactly one Figma Plugin API
// call. This file doesn't know what a "screen" or "component" is -- it only
// knows how to run create_page/create_frame/create_text/set_auto_layout/
// set_fill/create_component.

type Operation =
  | { type: "create_page"; ref: string; name: string; activate: boolean }
  | { type: "create_frame"; ref: string; parent_ref: string; name: string }
  | { type: "create_text"; ref: string; parent_ref: string; text: string; font_size: number; bold: boolean }
  | { type: "set_auto_layout"; ref: string; direction: "horizontal" | "vertical"; spacing: number; padding: number }
  | { type: "set_fill"; ref: string; r: number; g: number; b: number }
  | { type: "create_component"; ref: string };

interface FigmaRenderPlan {
  operations: Operation[];
  main_page_ref: string;
  screen_names: string[];
}

interface NextJobResponse {
  job_id: string | null;
  render_plan: FigmaRenderPlan | null;
}

interface PluginConfig {
  baseUrl: string;
  token: string;
}

let config: PluginConfig | null = null;
let polling = false;

figma.showUI(__html__, { width: 380, height: 460 });

figma.ui.onmessage = (msg: { type: string; baseUrl?: string; token?: string; intervalMs?: number }) => {
  if (msg.type === "start") {
    config = { baseUrl: msg.baseUrl || "http://127.0.0.1:8787", token: msg.token || "" };
    if (!polling) {
      polling = true;
      log("Polling started.");
      pollLoop(msg.intervalMs || 3000);
    }
  } else if (msg.type === "stop") {
    polling = false;
    log("Polling stopped.");
  }
};

function log(text: string): void {
  figma.ui.postMessage({ type: "log", text });
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function pollLoop(intervalMs: number): Promise<void> {
  while (polling) {
    try {
      await pollOnce();
    } catch (error) {
      log(`Poll error: ${error}`);
    }
    await sleep(intervalMs);
  }
}

async function pollOnce(): Promise<void> {
  if (!config) return;

  const response = await fetch(`${config.baseUrl}/figma/jobs/next`, {
    headers: { "X-Plugin-Token": config.token },
  });
  if (!response.ok) {
    log(`GET /figma/jobs/next failed: HTTP ${response.status}`);
    return;
  }

  const body: NextJobResponse = await response.json();
  if (!body.job_id || !body.render_plan) {
    return; // nothing pending -- stay quiet, this fires every poll tick
  }

  log(`Claimed job ${body.job_id} -- running ${body.render_plan.operations.length} operation(s)...`);
  try {
    const fileUrl = await runRenderPlan(body.render_plan);
    await reportComplete(body.job_id, fileUrl, body.render_plan.screen_names);
    log(`Job ${body.job_id} completed. Screens: ${body.render_plan.screen_names.join(", ") || "(none)"}`);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    log(`Job ${body.job_id} FAILED: ${message}`);
    await reportFail(body.job_id, message);
  }
}

async function reportComplete(jobId: string, fileUrl: string, builtScreens: string[]): Promise<void> {
  if (!config) return;
  const response = await fetch(`${config.baseUrl}/figma/jobs/${jobId}/complete`, {
    method: "POST",
    headers: { "X-Plugin-Token": config.token, "Content-Type": "application/json" },
    body: JSON.stringify({
      file_key: figma.fileKey || "",
      file_url: fileUrl,
      built_screens: builtScreens,
      notes: `Built via the Figma Plugin API (thin operation adapter) -- ${builtScreens.length} screen(s).`,
    }),
  });
  if (!response.ok) log(`complete report failed: HTTP ${response.status}`);
}

async function reportFail(jobId: string, error: string): Promise<void> {
  if (!config) return;
  const response = await fetch(`${config.baseUrl}/figma/jobs/${jobId}/fail`, {
    method: "POST",
    headers: { "X-Plugin-Token": config.token, "Content-Type": "application/json" },
    body: JSON.stringify({ error }),
  });
  if (!response.ok) log(`fail report failed: HTTP ${response.status}`);
}

// --- Operation interpreter ----------------------------------------------

type ContainerNode = PageNode | FrameNode | ComponentNode;

function getContainer(refs: Map<string, BaseNode>, ref: string, opDescription: string): ContainerNode {
  const node = refs.get(ref);
  if (!node) throw new Error(`${opDescription}: unknown ref "${ref}"`);
  if (node.type !== "PAGE" && node.type !== "FRAME" && node.type !== "COMPONENT") {
    throw new Error(`${opDescription}: ref "${ref}" is a ${node.type}, not a container`);
  }
  return node as ContainerNode;
}

function getFrame(refs: Map<string, BaseNode>, ref: string, opDescription: string): FrameNode {
  const node = refs.get(ref);
  if (!node) throw new Error(`${opDescription}: unknown ref "${ref}"`);
  if (node.type !== "FRAME") throw new Error(`${opDescription}: ref "${ref}" is a ${node.type}, not a frame`);
  return node as FrameNode;
}

async function applyOperation(op: Operation, refs: Map<string, BaseNode>): Promise<void> {
  switch (op.type) {
    case "create_page": {
      const page = figma.createPage();
      page.name = op.name;
      refs.set(op.ref, page);
      if (op.activate) await figma.setCurrentPageAsync(page);
      return;
    }
    case "create_frame": {
      const frame = figma.createFrame();
      frame.name = op.name;
      getContainer(refs, op.parent_ref, `create_frame ${op.ref}`).appendChild(frame);
      refs.set(op.ref, frame);
      return;
    }
    case "create_text": {
      const text = figma.createText();
      text.fontName = { family: "Inter", style: op.bold ? "Bold" : "Regular" };
      text.fontSize = op.font_size;
      text.characters = op.text;
      getContainer(refs, op.parent_ref, `create_text ${op.ref}`).appendChild(text);
      refs.set(op.ref, text);
      return;
    }
    case "set_auto_layout": {
      const frame = getFrame(refs, op.ref, "set_auto_layout");
      frame.layoutMode = op.direction === "horizontal" ? "HORIZONTAL" : "VERTICAL";
      frame.primaryAxisSizingMode = "AUTO";
      frame.counterAxisSizingMode = "AUTO";
      frame.itemSpacing = op.spacing;
      frame.paddingTop = op.padding;
      frame.paddingBottom = op.padding;
      frame.paddingLeft = op.padding;
      frame.paddingRight = op.padding;
      return;
    }
    case "set_fill": {
      const frame = getFrame(refs, op.ref, "set_fill");
      frame.fills = [{ type: "SOLID", color: { r: op.r, g: op.g, b: op.b } }];
      return;
    }
    case "create_component": {
      const frame = getFrame(refs, op.ref, "create_component");
      const component = figma.createComponentFromNode(frame);
      refs.set(op.ref, component);
      return;
    }
  }
}

async function runRenderPlan(plan: FigmaRenderPlan): Promise<string> {
  await figma.loadFontAsync({ family: "Inter", style: "Regular" });
  await figma.loadFontAsync({ family: "Inter", style: "Bold" });

  const refs = new Map<string, BaseNode>();
  for (let i = 0; i < plan.operations.length; i++) {
    const op = plan.operations[i];
    try {
      await applyOperation(op, refs);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      throw new Error(`operation ${i} (${op.type}, ref=${op.ref}) failed: ${message}`);
    }
  }

  if (!figma.fileKey) {
    throw new Error(
      "This file has no fileKey -- open a saved Figma Cloud file (not an unsaved local draft) before running the plugin."
    );
  }
  const mainPage = refs.get(plan.main_page_ref);
  const nodeId = mainPage ? mainPage.id : "";
  return `https://www.figma.com/design/${figma.fileKey}?node-id=${encodeURIComponent(nodeId)}`;
}
