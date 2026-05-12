const defaultState = {
  projectId: "bridge_001",
  startStation: "K0+000",
  spans: "40,70,40",
  deckWidth: 7.5,
  sectionType: "single_box_single_cell",
  pierType: "double_column",
  abutmentType: "gravity",
  girderDepthPolicy: "auto",
  girderDepth: 2.5,
  drawings: ["general_arrangement", "plan", "elevation", "typical_section"],
};

const samplePrompts = [
  "画一座40+70+40米跨径、桥宽7.5米的预应力连续梁桥，采用单箱单室，双柱墩，重力式桥台。",
  "画一座60+100+60米跨径、桥宽12米的预应力连续梁桥，采用单箱双室，实体墩，桥台采用搭板式。",
  "Draw a prestressed continuous girder bridge with spans 30+50+30 m, deck width 9.5 m, double-column piers, gravity abutments, and manual girder depth 3.2 m.",
];
const samplePatches = [
  "把中跨改成75米。",
  "桥宽改成9米，采用单箱双室。",
  "Change the middle span to 90 m and use solid piers.",
];

const layerStyles = {
  BRIDGE_GIRDER: { stroke: "#1f2937", fill: "none" },
  BRIDGE_DECK: { stroke: "#0f766e", fill: "rgba(15, 118, 110, 0.12)" },
  BRIDGE_SECTION: { stroke: "#b45309", fill: "rgba(180, 83, 9, 0.10)" },
  DIM: { stroke: "#64748b", fill: "none" },
  TEXT: { stroke: "none", fill: "#111827" },
};

const padding = 16;
let latestSvg = "";
let latestBridgeModel = null;
let latestInstructionBatch = null;
let latestAssumptions = [];
let latestPatchSummary = [];
let selectedDrawings = [...defaultState.drawings];
let samplePromptIndex = 0;
let samplePatchIndex = 0;
let busyCount = 0;
const requestLogEntries = [];
const defaultButtonLabels = {};

const elements = {
  promptInput: document.getElementById("promptInput"),
  parsePromptButton: document.getElementById("parsePromptButton"),
  samplePromptButton: document.getElementById("samplePromptButton"),
  assumptionList: document.getElementById("assumptionList"),
  patchPromptInput: document.getElementById("patchPromptInput"),
  applyPatchButton: document.getElementById("applyPatchButton"),
  samplePatchButton: document.getElementById("samplePatchButton"),
  patchSummaryList: document.getElementById("patchSummaryList"),
  parserMode: document.getElementById("parserMode"),
  serviceUrl: document.getElementById("serviceUrl"),
  ollamaModel: document.getElementById("ollamaModel"),
  projectId: document.getElementById("projectId"),
  startStation: document.getElementById("startStation"),
  spans: document.getElementById("spans"),
  deckWidth: document.getElementById("deckWidth"),
  sectionType: document.getElementById("sectionType"),
  pierType: document.getElementById("pierType"),
  abutmentType: document.getElementById("abutmentType"),
  girderDepthPolicy: document.getElementById("girderDepthPolicy"),
  girderDepth: document.getElementById("girderDepth"),
  girderDepthField: document.getElementById("girderDepthField"),
  drawingPlan: document.getElementById("drawingPlan"),
  drawingElevation: document.getElementById("drawingElevation"),
  drawingSection: document.getElementById("drawingSection"),
  drawingSummaryText: document.getElementById("drawingSummaryText"),
  regenerateButton: document.getElementById("regenerateButton"),
  resetButton: document.getElementById("resetButton"),
  downloadSvgButton: document.getElementById("downloadSvgButton"),
  downloadModelButton: document.getElementById("downloadModelButton"),
  previewViewport: document.getElementById("previewViewport"),
  bridgeModelOutput: document.getElementById("bridgeModelOutput"),
  instructionOutput: document.getElementById("instructionOutput"),
  statusText: document.getElementById("statusText"),
  requestLog: document.getElementById("requestLog"),
  busyBadge: document.getElementById("busyBadge"),
  lastModeText: document.getElementById("lastModeText"),
};

[
  "parsePromptButton",
  "samplePromptButton",
  "applyPatchButton",
  "samplePatchButton",
  "regenerateButton",
  "resetButton",
].forEach((key) => {
  defaultButtonLabels[key] = elements[key].textContent.trim();
});

function applyDefaultState() {
  selectedDrawings = [...defaultState.drawings];
  elements.promptInput.value = samplePrompts[0];
  elements.patchPromptInput.value = samplePatches[0];
  elements.parserMode.value = "local";
  elements.serviceUrl.value = "http://127.0.0.1:8011";
  elements.ollamaModel.value = "glm-4.7:cloud";
  elements.projectId.value = defaultState.projectId;
  elements.startStation.value = defaultState.startStation;
  elements.spans.value = defaultState.spans;
  elements.deckWidth.value = String(defaultState.deckWidth);
  elements.sectionType.value = defaultState.sectionType;
  elements.pierType.value = defaultState.pierType;
  elements.abutmentType.value = defaultState.abutmentType;
  elements.girderDepthPolicy.value = defaultState.girderDepthPolicy;
  elements.girderDepth.value = String(defaultState.girderDepth);
  syncDepthField();
  syncDrawingControls();
}

function updateAssumptions(items) {
  latestAssumptions = items;
  elements.assumptionList.innerHTML = "";
  items.forEach((item) => {
    const row = document.createElement("li");
    row.textContent = item;
    elements.assumptionList.appendChild(row);
  });
}

function updatePatchSummary(items) {
  latestPatchSummary = items;
  elements.patchSummaryList.innerHTML = "";
  items.forEach((item) => {
    const row = document.createElement("li");
    row.textContent = item;
    elements.patchSummaryList.appendChild(row);
  });
}

function timestamp() {
  return new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function logEvent(message) {
  requestLogEntries.unshift(`${timestamp()}  ${message}`);
  requestLogEntries.splice(8);
  elements.requestLog.innerHTML = "";
  requestLogEntries.forEach((entry) => {
    const item = document.createElement("li");
    item.textContent = entry;
    elements.requestLog.appendChild(item);
  });
}

function setBusy(active, label, buttonKeys = []) {
  busyCount += active ? 1 : -1;
  if (busyCount < 0) {
    busyCount = 0;
  }
  const busy = busyCount > 0;
  elements.busyBadge.textContent = busy ? label || "Working" : "Idle";
  elements.busyBadge.className = `busy-badge ${busy ? "busy" : "idle"}`;
  buttonKeys.forEach((key) => {
    elements[key].disabled = active;
    elements[key].textContent = active ? label : defaultButtonLabels[key];
  });
}

function syncDepthField() {
  const manual = elements.girderDepthPolicy.value === "manual";
  elements.girderDepthField.style.display = manual ? "flex" : "none";
}

function parseSpans(rawValue) {
  return rawValue
    .split(",")
    .map((part) => Number(part.trim()))
    .filter((value) => !Number.isNaN(value));
}

function normalizeDrawings(drawings) {
  const allowed = ["general_arrangement", "plan", "elevation", "typical_section"];
  const values = Array.isArray(drawings)
    ? drawings.filter((item) => typeof item === "string" && allowed.includes(item))
    : [];
  return values.length > 0 ? Array.from(new Set(values)) : [...defaultState.drawings];
}

function ensureGeneralArrangement(drawings) {
  const normalized = normalizeDrawings(drawings).filter((item) => item !== "general_arrangement");
  return ["general_arrangement", ...normalized];
}

function formatDrawingLabel(drawing) {
  if (drawing === "general_arrangement") {
    return "general arrangement";
  }
  if (drawing === "typical_section") {
    return "typical section";
  }
  return drawing;
}

function syncDrawingControls() {
  const drawings = ensureGeneralArrangement(selectedDrawings);
  selectedDrawings = drawings;
  elements.drawingPlan.checked = drawings.includes("plan");
  elements.drawingElevation.checked = drawings.includes("elevation");
  elements.drawingSection.checked = drawings.includes("typical_section");
  elements.drawingSummaryText.textContent = drawings.map(formatDrawingLabel).join(", ");
}

function detectRequestedDrawings(text) {
  const normalized = text.toLowerCase();
  const include = new Set();
  const exclude = new Set();

  if (/(只|仅|only).*(断面图|横断面|截面图|section)/i.test(normalized)) {
    return ["general_arrangement", "typical_section"];
  }
  if (/(只|仅|only).*(平面图|plan)/i.test(normalized)) {
    return ["general_arrangement", "plan"];
  }
  if (/(只|仅|only).*(立面图|elevation)/i.test(normalized)) {
    return ["general_arrangement", "elevation"];
  }

  if (/总图|general arrangement|ga drawing/i.test(normalized)) {
    include.add("general_arrangement");
  }
  if (/平面图|plan view|plan\b/i.test(normalized)) {
    include.add("plan");
  }
  if (/立面图|elevation view|elevation\b/i.test(normalized)) {
    include.add("elevation");
  }
  if (/断面图|横断面|截面图|typical section|section view|\bsection\b/i.test(normalized)) {
    include.add("typical_section");
  }

  if (/(不要|不出|去掉|取消|remove|without|exclude|drop).*(平面图|plan)/i.test(normalized)) {
    exclude.add("plan");
  }
  if (/(不要|不出|去掉|取消|remove|without|exclude|drop).*(立面图|elevation)/i.test(normalized)) {
    exclude.add("elevation");
  }
  if (/(不要|不出|去掉|取消|remove|without|exclude|drop).*(断面图|横断面|截面图|section)/i.test(normalized)) {
    exclude.add("typical_section");
  }

  if (include.size === 0 && exclude.size === 0) {
    return null;
  }

  const requested = exclude.size > 0 ? new Set(defaultState.drawings) : new Set(["general_arrangement"]);
  include.forEach((item) => requested.add(item));
  exclude.forEach((item) => requested.delete(item));
  if (![...requested].some((item) => item !== "general_arrangement")) {
    requested.add("plan");
    requested.add("elevation");
    requested.add("typical_section");
  }
  return normalizeDrawings(Array.from(requested));
}

function parsePrompt(prompt) {
  const text = prompt.trim();
  if (!text) {
    throw new Error("Enter a bridge description before parsing.");
  }

  const assumptions = [];
  const parsed = {};
  const normalized = text
    .replaceAll("＋", "+")
    .replaceAll("，", ",")
    .replaceAll("。", ".")
    .replaceAll("米", "m");

  const spanMatch = normalized.match(/(\d+(?:\.\d+)?(?:\s*\+\s*\d+(?:\.\d+)?)+)\s*m?(?:跨径|span|spans?)/i);
  if (spanMatch) {
    parsed.spans = spanMatch[1]
      .split("+")
      .map((part) => Number(part.trim()))
      .filter((value) => !Number.isNaN(value));
  } else {
    assumptions.push("Spans were not detected, so the existing span values were kept.");
  }

  const widthMatch =
    normalized.match(/桥宽\s*(\d+(?:\.\d+)?)\s*m/i) ||
    normalized.match(/width\s*(?:of)?\s*(\d+(?:\.\d+)?)\s*m/i) ||
    normalized.match(/deck width\s*(\d+(?:\.\d+)?)\s*m/i);
  if (widthMatch) {
    parsed.deckWidth = Number(widthMatch[1]);
  } else {
    assumptions.push("Deck width was not detected, so the existing width was kept.");
  }

  if (/单箱双室|double cell/i.test(normalized)) {
    parsed.sectionType = "single_box_double_cell";
  } else if (/单箱单室|single cell/i.test(normalized)) {
    parsed.sectionType = "single_box_single_cell";
  } else {
    assumptions.push("Section type was not detected, so the existing section type was kept.");
  }

  if (/实体墩|solid pier/i.test(normalized)) {
    parsed.pierType = "solid_pier";
  } else if (/双柱墩|double[- ]column/i.test(normalized)) {
    parsed.pierType = "double_column";
  } else {
    assumptions.push("Pier type was not detected, so the existing pier type was kept.");
  }

  if (/搭板|seat abutment|seat/i.test(normalized)) {
    parsed.abutmentType = "seat";
  } else if (/重力式|gravity/i.test(normalized)) {
    parsed.abutmentType = "gravity";
  } else {
    assumptions.push("Abutment type was not detected, so the existing abutment type was kept.");
  }

  const stationMatch = normalized.match(/K\d+\+\d+/i);
  if (stationMatch) {
    parsed.startStation = stationMatch[0].toUpperCase();
  } else {
    assumptions.push("Start station was not detected, so the existing station was kept.");
  }

  const manualDepthMatch = normalized.match(/(?:梁高|girder depth)\s*(\d+(?:\.\d+)?)\s*m/i);
  if (manualDepthMatch) {
    parsed.girderDepthPolicy = "manual";
    parsed.girderDepth = Number(manualDepthMatch[1]);
  } else {
    parsed.girderDepthPolicy = "auto";
    assumptions.push("Girder depth was not specified, so automatic depth was used.");
  }

  const requestedDrawings = detectRequestedDrawings(normalized);
  if (requestedDrawings) {
    parsed.drawings = requestedDrawings;
  } else {
    assumptions.push("Requested drawings were not detected, so the existing drawing selection was kept.");
  }

  assumptions.unshift("Bridge type is assumed to be a prestressed continuous girder bridge.");
  return { parsed, assumptions };
}

function applyParsedPrompt(result) {
  const { parsed, assumptions } = result;
  if (parsed.spans && parsed.spans.length > 0) {
    elements.spans.value = parsed.spans.join(",");
  }
  if (parsed.deckWidth) {
    elements.deckWidth.value = String(parsed.deckWidth);
  }
  if (parsed.sectionType) {
    elements.sectionType.value = parsed.sectionType;
  }
  if (parsed.pierType) {
    elements.pierType.value = parsed.pierType;
  }
  if (parsed.abutmentType) {
    elements.abutmentType.value = parsed.abutmentType;
  }
  if (parsed.startStation) {
    elements.startStation.value = parsed.startStation;
  }
  if (parsed.girderDepthPolicy) {
    elements.girderDepthPolicy.value = parsed.girderDepthPolicy;
  }
  if (parsed.girderDepth) {
    elements.girderDepth.value = String(parsed.girderDepth);
  }
  if (parsed.drawings) {
    selectedDrawings = ensureGeneralArrangement(parsed.drawings);
  }
  syncDepthField();
  syncDrawingControls();
  updateAssumptions(assumptions);
}

function applyIntentPayload(payload) {
  const intent = payload.intent || {};
  if (Array.isArray(intent.spans_m) && intent.spans_m.length > 0) {
    elements.spans.value = intent.spans_m.join(",");
  }
  if (typeof intent.deck_width_m === "number") {
    elements.deckWidth.value = String(intent.deck_width_m);
  }
  if (intent.alignment_type) {
    elements.startStation.value = intent.start_station || elements.startStation.value;
  }
  if (intent.superstructure?.section_type) {
    elements.sectionType.value = intent.superstructure.section_type;
  }
  if (intent.superstructure?.girder_depth_policy) {
    elements.girderDepthPolicy.value = intent.superstructure.girder_depth_policy;
  }
  if (typeof intent.superstructure?.girder_depth_m === "number") {
    elements.girderDepth.value = String(intent.superstructure.girder_depth_m);
  }
  if (intent.substructure?.pier_type) {
    elements.pierType.value = intent.substructure.pier_type;
  }
  if (intent.substructure?.abutment_type) {
    elements.abutmentType.value = intent.substructure.abutment_type;
  }
  if (Array.isArray(intent.requested_drawings)) {
    selectedDrawings = ensureGeneralArrangement(intent.requested_drawings);
  }
  syncDepthField();
  syncDrawingControls();
  updateAssumptions(payload.assumptions || []);
}

function applyPatchLocally(bridgeModel, patchResponse) {
  const nextModel = JSON.parse(JSON.stringify(bridgeModel));
  for (const patch of patchResponse.patches || []) {
    if (patch.op !== "replace") {
      continue;
    }
    applyReplacePatch(nextModel, patch.path, patch.value);
  }
  return nextModel;
}

function applyReplacePatch(target, path, value) {
  const segments = path
    .split("/")
    .filter(Boolean)
    .map((segment) => (/^\d+$/.test(segment) ? Number(segment) : segment));

  if (segments.length === 0) {
    return;
  }

  let current = target;
  for (let index = 0; index < segments.length - 1; index += 1) {
    current = current[segments[index]];
    if (current === undefined || current === null) {
      return;
    }
  }

  current[segments[segments.length - 1]] = value;
}

function createLocalPatchResponse(bridgeModel, prompt) {
  const patches = [];
  const affectedViews = new Set();
  const summary = [];
  const text = prompt.trim();

  if (!text) {
    throw new Error("Enter an edit instruction before applying a patch.");
  }

  const normalized = text.replaceAll("＋", "+").replaceAll("，", ",").replaceAll("。", ".");

  const middleSpanMatch = normalized.match(/(?:middle span|中跨)(?:改成|to|=)?\s*(\d+(?:\.\d+)?)\s*m?/i);
  if (middleSpanMatch && bridgeModel.bridge.spans_m.length >= 3) {
    const middle = Number(middleSpanMatch[1]);
    patches.push({ op: "replace", path: "/bridge/spans_m/1", value: middle });
    affectedViews.add("plan");
    affectedViews.add("elevation");
    affectedViews.add("typical_section");
    summary.push(`Middle span updated to ${middle} m.`);
  }

  const widthMatch =
    normalized.match(/桥宽\s*(?:改成)?\s*(\d+(?:\.\d+)?)\s*m?/i) ||
    normalized.match(/(?:deck width|width)(?:\s+to)?\s*(\d+(?:\.\d+)?)\s*m/i);
  if (widthMatch) {
    const width = Number(widthMatch[1]);
    patches.push({ op: "replace", path: "/bridge/deck_width_m", value: width });
    affectedViews.add("plan");
    affectedViews.add("typical_section");
    summary.push(`Deck width updated to ${width} m.`);
  }

  if (/单箱双室|double cell/i.test(normalized)) {
    patches.push({
      op: "replace",
      path: "/bridge/superstructure/section_type",
      value: "single_box_double_cell",
    });
    affectedViews.add("typical_section");
    summary.push("Section type updated to single-box double-cell.");
  } else if (/单箱单室|single cell/i.test(normalized)) {
    patches.push({
      op: "replace",
      path: "/bridge/superstructure/section_type",
      value: "single_box_single_cell",
    });
    affectedViews.add("typical_section");
    summary.push("Section type updated to single-box single-cell.");
  }

  if (/实体墩|solid pier/i.test(normalized)) {
    patches.push({
      op: "replace",
      path: "/bridge/substructure/pier_type",
      value: "solid_pier",
    });
    affectedViews.add("elevation");
    summary.push("Pier type updated to solid pier.");
  } else if (/双柱墩|double[- ]column/i.test(normalized)) {
    patches.push({
      op: "replace",
      path: "/bridge/substructure/pier_type",
      value: "double_column",
    });
    affectedViews.add("elevation");
    summary.push("Pier type updated to double-column.");
  }

    const requestedDrawings = detectRequestedDrawings(normalized);
  if (requestedDrawings) {
    const currentDrawings = ensureGeneralArrangement(bridgeModel.bridge.drawings);
    const nextDrawings = ensureGeneralArrangement(requestedDrawings);
    if (JSON.stringify(currentDrawings) !== JSON.stringify(nextDrawings)) {
      patches.push({ op: "replace", path: "/bridge/drawings", value: nextDrawings });
      ["plan", "elevation", "typical_section"].forEach((view) => {
        if (currentDrawings.includes(view) || nextDrawings.includes(view)) {
          affectedViews.add(view);
        }
      });
      summary.push(`Requested drawings updated to ${nextDrawings.map(formatDrawingLabel).join(", ")}.`);
    }
  }

  if (patches.length === 0) {
    throw new Error("No supported model edits were detected in the patch instruction.");
  }

  return {
    patches,
    affected_views: Array.from(affectedViews).sort(),
    summary,
  };
}

function buildBridgeModel() {
  const spans = parseSpans(elements.spans.value);
  const deckWidth = Number(elements.deckWidth.value);

  if (spans.length === 0 || spans.some((span) => span <= 0)) {
    throw new Error("Spans must be a comma-separated list of positive numbers.");
  }

  if (!Number.isFinite(deckWidth) || deckWidth <= 0) {
    throw new Error("Deck width must be a positive number.");
  }

  const girderDepthPolicy = elements.girderDepthPolicy.value;
  const bridgeModel = {
    project_id: elements.projectId.value.trim() || "bridge_preview",
    bridge: {
      type: "continuous_girder",
      material: "prestressed_concrete",
      spans_m: spans,
      deck_width_m: deckWidth,
      alignment: {
        type: "straight",
        start_station: elements.startStation.value.trim() || "K0+000",
      },
      superstructure: {
        section_type: elements.sectionType.value,
        girder_depth_policy: girderDepthPolicy,
      },
      substructure: {
        pier_type: elements.pierType.value,
        abutment_type: elements.abutmentType.value,
      },
      drawings: ensureGeneralArrangement(selectedDrawings),
    },
  };

  if (girderDepthPolicy === "manual") {
    const depth = Number(elements.girderDepth.value);
    if (!Number.isFinite(depth) || depth <= 0) {
      throw new Error("Girder depth must be a positive number in manual mode.");
    }
    bridgeModel.bridge.superstructure.girder_depth_m = depth;
  }

  return bridgeModel;
}

function createDrawingPlan(bridgeModel) {
  const requestedDrawings = ensureGeneralArrangement(bridgeModel.bridge.drawings);
  const selectedTypes = new Set(
    requestedDrawings.filter((drawing) => drawing === "plan" || drawing === "elevation" || drawing === "typical_section")
  );
  if (selectedTypes.size === 0) {
    selectedTypes.add("plan");
    selectedTypes.add("elevation");
    selectedTypes.add("typical_section");
  }

  return {
    project_id: bridgeModel.project_id,
    drawing_id: "general_arrangement_001",
    drawing_type: "general_arrangement",
    sheet: {
      size: "A1",
      scale: 200,
    },
    views: [
      { view_id: "elevation_main", type: "elevation", origin: [0, 0], scale: 200 },
      { view_id: "plan_main", type: "plan", origin: [0, -120], scale: 200 },
      {
        view_id: "typical_section_main",
        type: "typical_section",
        origin: [190, 0],
        scale: 100,
      },
    ].filter((view) => selectedTypes.has(view.type)),
  };
}

function normalizeNumber(value) {
  return Number.isInteger(value) ? value : Number(value.toFixed(3));
}

function cumulativeSpanPoints(spans) {
  const points = [0];
  let running = 0;
  for (const span of spans) {
    running += span;
    points.push(normalizeNumber(running));
  }
  return points;
}

function resolveSectionDepth(bridgeModel) {
  const superstructure = bridgeModel.bridge.superstructure;
  if (superstructure.girder_depth_policy === "manual") {
    return superstructure.girder_depth_m;
  }
  return 2.5;
}

function formatLength(length) {
  return Number.isInteger(length) ? String(length) : String(length);
}

function createCadInstructionBatch(bridgeModel, drawingPlan) {
  const views = Object.fromEntries(drawingPlan.views.map((view) => [view.view_id, view]));
  const spans = bridgeModel.bridge.spans_m;
  const spanPoints = cumulativeSpanPoints(spans);
  const totalLength = spans.reduce((sum, span) => sum + span, 0);
  const depth = resolveSectionDepth(bridgeModel);
  const instructions = [];

  if (views.elevation_main) {
    const elevationOrigin = views.elevation_main.origin;
    instructions.push({
      kind: "polyline",
      id: "elevation_girder_bottom",
      layer: "BRIDGE_GIRDER",
      view_id: "elevation_main",
      source_component_id: "main_girder",
      points: spanPoints.map((point) => [normalizeNumber(elevationOrigin[0] + point), elevationOrigin[1]]),
      closed: false,
    });
    spans.forEach((span, index) => {
      const start = spanPoints[index];
      const end = spanPoints[index + 1];
      instructions.push({
        kind: "aligned_dimension",
        id: `dim_span_${index + 1}`,
        layer: "DIM",
        view_id: "elevation_main",
        source_component_id: `span_${index + 1}`,
        from: [normalizeNumber(elevationOrigin[0] + start), normalizeNumber(elevationOrigin[1] - 5)],
        to: [normalizeNumber(elevationOrigin[0] + end), normalizeNumber(elevationOrigin[1] - 5)],
        dimension_line_point: [
          normalizeNumber(elevationOrigin[0] + (start + end) / 2),
          normalizeNumber(elevationOrigin[1] - 12),
        ],
        text: `${formatLength(span)}m`,
      });
    });
  }

  if (views.plan_main) {
    const planOrigin = views.plan_main.origin;
    const halfWidth = bridgeModel.bridge.deck_width_m / 2;
    instructions.push({
      kind: "polyline",
      id: "plan_deck_outline",
      layer: "BRIDGE_DECK",
      view_id: "plan_main",
      source_component_id: "deck_outline",
      points: [
        [planOrigin[0], normalizeNumber(planOrigin[1] - halfWidth)],
        [normalizeNumber(planOrigin[0] + totalLength), normalizeNumber(planOrigin[1] - halfWidth)],
        [normalizeNumber(planOrigin[0] + totalLength), normalizeNumber(planOrigin[1] + halfWidth)],
        [planOrigin[0], normalizeNumber(planOrigin[1] + halfWidth)],
      ],
      closed: true,
    });
  }

  if (views.typical_section_main) {
    const sectionOrigin = views.typical_section_main.origin;
    instructions.push({
      kind: "polyline",
      id: "typical_section_outline",
      layer: "BRIDGE_SECTION",
      view_id: "typical_section_main",
      source_component_id: "typical_section",
      points: [
        [sectionOrigin[0], sectionOrigin[1]],
        [normalizeNumber(sectionOrigin[0] + bridgeModel.bridge.deck_width_m), sectionOrigin[1]],
        [
          normalizeNumber(sectionOrigin[0] + bridgeModel.bridge.deck_width_m),
          normalizeNumber(sectionOrigin[1] - depth),
        ],
        [sectionOrigin[0], normalizeNumber(sectionOrigin[1] - depth)],
      ],
      closed: true,
    });
  }

  const titleView = views.elevation_main || views.plan_main || views.typical_section_main;
  if (titleView) {
    instructions.push({
      kind: "text",
      id: "title_general_arrangement",
      layer: "TEXT",
      view_id: titleView.view_id,
      source_component_id: "drawing_title",
      position: [titleView.origin[0], normalizeNumber(titleView.origin[1] + 10)],
      text: "GENERAL ARRANGEMENT",
      height: 3.5,
    });
  }

  return {
    project_id: drawingPlan.project_id,
    drawing_id: drawingPlan.drawing_id,
    instructions,
  };
}

function instructionPoints(instruction) {
  if (instruction.kind === "polyline") {
    return instruction.points;
  }
  if (instruction.kind === "line") {
    return [instruction.from, instruction.to];
  }
  if (instruction.kind === "text") {
    return [instruction.position];
  }
  if (instruction.kind === "aligned_dimension") {
    return [instruction.from, instruction.to, instruction.dimension_line_point];
  }
  return [];
}

function computeBounds(instructions) {
  const xs = [];
  const ys = [];

  instructions.forEach((instruction) => {
    instructionPoints(instruction).forEach((point) => {
      xs.push(point[0]);
      ys.push(point[1]);
    });
  });

  return {
    minX: Math.min(...xs),
    minY: Math.min(...ys),
    maxX: Math.max(...xs),
    maxY: Math.max(...ys),
  };
}

function mapPoint(point, bounds) {
  return {
    x: point[0] - bounds.minX + padding,
    y: bounds.maxY - point[1] + padding,
  };
}

function renderInstruction(instruction, bounds) {
  const style = layerStyles[instruction.layer] || { stroke: "#334155", fill: "none" };

  if (instruction.kind === "polyline") {
    const points = instruction.points
      .map((point) => {
        const mapped = mapPoint(point, bounds);
        return `${mapped.x},${mapped.y}`;
      })
      .join(" ");
    return `<polyline points="${points}" stroke="${style.stroke}" fill="${
      instruction.closed ? style.fill : "none"
    }" stroke-width="1.5" />`;
  }

  if (instruction.kind === "text") {
    const position = mapPoint(instruction.position, bounds);
    return `<text x="${position.x}" y="${position.y - 4}" fill="${style.fill}" font-family="Consolas, monospace" font-size="${
      instruction.height * 3
    }">${escapeHtml(instruction.text)}</text>`;
  }

  if (instruction.kind === "aligned_dimension") {
    const from = mapPoint(instruction.from, bounds);
    const to = mapPoint(instruction.to, bounds);
    const dim = mapPoint(instruction.dimension_line_point, bounds);
    return [
      `<line x1="${from.x}" y1="${from.y}" x2="${to.x}" y2="${to.y}" stroke="${style.stroke}" stroke-width="1" stroke-dasharray="4 2" />`,
      `<text x="${dim.x}" y="${dim.y - 4}" fill="${style.stroke}" font-family="Consolas, monospace" font-size="10" text-anchor="middle">${escapeHtml(
        instruction.text
      )}</text>`,
    ].join("");
  }

  if (instruction.kind === "line") {
    const from = mapPoint(instruction.from, bounds);
    const to = mapPoint(instruction.to, bounds);
    return `<line x1="${from.x}" y1="${from.y}" x2="${to.x}" y2="${to.y}" stroke="${style.stroke}" stroke-width="1.5" />`;
  }

  return "";
}

function renderSvgDocument(instructionBatch) {
  if (!instructionBatch.instructions.length) {
    return `
      <svg xmlns="http://www.w3.org/2000/svg" width="480" height="160" viewBox="0 0 480 160" role="img" aria-label="VibeDraw preview">
        <rect width="480" height="160" fill="#f8fafc"></rect>
        <text x="24" y="72" fill="#111827" font-family="Consolas, monospace" font-size="18">No drawable views are currently selected.</text>
      </svg>
    `.trim();
  }

  const bounds = computeBounds(instructionBatch.instructions);
  const width = Math.max(Math.ceil(bounds.maxX - bounds.minX + padding * 2), 1);
  const height = Math.max(Math.ceil(bounds.maxY - bounds.minY + padding * 2), 1);
  const body = instructionBatch.instructions.map((instruction) => renderInstruction(instruction, bounds)).join("");

  return `
    <svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" role="img" aria-label="VibeDraw preview">
      <rect width="${width}" height="${height}" fill="#f8fafc"></rect>
      ${body}
    </svg>
  `.trim();
}

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function updateOutputs(bridgeModel, instructionBatch, svg) {
  latestBridgeModel = bridgeModel;
  latestInstructionBatch = instructionBatch;
  latestSvg = svg;
  elements.previewViewport.innerHTML = svg;
  elements.bridgeModelOutput.textContent = JSON.stringify(bridgeModel, null, 2);
  elements.instructionOutput.textContent = JSON.stringify(instructionBatch, null, 2);
}

function regenerate() {
  try {
    const bridgeModel = buildBridgeModel();
    selectedDrawings = ensureGeneralArrangement(bridgeModel.bridge.drawings);
    syncDrawingControls();
    const drawingPlan = createDrawingPlan(bridgeModel);
    const instructionBatch = createCadInstructionBatch(bridgeModel, drawingPlan);
    const svg = renderSvgDocument(instructionBatch);
    updateOutputs(bridgeModel, instructionBatch, svg);
    elements.statusText.textContent = `Preview regenerated for ${bridgeModel.bridge.drawings.map(formatDrawingLabel).join(", ")} with spans ${bridgeModel.bridge.spans_m.join(" + ")} m and width ${bridgeModel.bridge.deck_width_m} m.`;
    logEvent(`Preview regenerated for project ${bridgeModel.project_id}.`);
  } catch (error) {
    elements.statusText.textContent = error.message;
    logEvent(`Preview regeneration failed: ${error.message}`);
  }
}

async function parsePromptIntoForm() {
  const mode = elements.parserMode.value;
  elements.lastModeText.textContent = `Mode: ${mode}`;
  setBusy(true, "Parsing...", ["parsePromptButton", "samplePromptButton"]);
  try {
    if (mode === "local") {
      logEvent("Parsing prompt locally.");
      const result = parsePrompt(elements.promptInput.value);
      applyParsedPrompt(result);
      regenerate();
      elements.statusText.textContent = `Prompt parsed locally. ${result.assumptions.length} assumption(s) noted.`;
      logEvent(`Local parser filled parameters with ${result.assumptions.length} assumption(s).`);
      return;
    }

    const serviceUrl = elements.serviceUrl.value.trim().replace(/\/$/, "");
    const model = elements.ollamaModel.value.trim();
    const query = new URLSearchParams();
    query.set("mode", mode);
    if (mode === "ollama") {
      if (!model) {
        throw new Error("Provide an Ollama model name before using ollama mode.");
      }
      query.set("model", model);
    }

    logEvent(`Sending parse request to ${serviceUrl} using mode=${mode}${mode === "ollama" ? ` model=${model}` : ""}.`);

    const response = await fetch(`${serviceUrl}/intent/parse-initial?${query.toString()}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        type: "parse_initial_intent",
        prompt: elements.promptInput.value,
      }),
    });

    const payload = await response.json();
    logEvent(`Service responded with status ${response.status}.`);
    if (!response.ok) {
      throw new Error(payload.error || "The LLM service request failed.");
    }

    applyIntentPayload(payload);
    regenerate();
    const label = mode === "mock" ? "LLM service mock" : `Ollama model ${model}`;
    elements.statusText.textContent = `Prompt parsed via ${label}. ${(payload.assumptions || []).length} assumption(s) noted.`;
    logEvent(`Applied intent payload from ${label}.`);
  } catch (error) {
    elements.statusText.textContent = error.message;
    logEvent(`Parse request failed: ${error.message}`);
  } finally {
    setBusy(false, "", ["parsePromptButton", "samplePromptButton"]);
  }
}

async function applyPatchPrompt() {
  const mode = elements.parserMode.value;
  elements.lastModeText.textContent = `Mode: ${mode}`;
  setBusy(true, "Patching...", ["applyPatchButton", "samplePatchButton"]);
  try {
    if (!latestBridgeModel) {
      throw new Error("Generate a bridge model before applying a patch.");
    }

    let patchResponse;

    if (mode === "local") {
      logEvent("Applying patch locally.");
      patchResponse = createLocalPatchResponse(latestBridgeModel, elements.patchPromptInput.value);
    } else {
      const serviceUrl = elements.serviceUrl.value.trim().replace(/\/$/, "");
      const model = elements.ollamaModel.value.trim();
      const query = new URLSearchParams();
      query.set("mode", mode);
      if (mode === "ollama") {
        if (!model) {
          throw new Error("Provide an Ollama model name before using ollama mode.");
        }
        query.set("model", model);
      }

      logEvent(`Sending patch request to ${serviceUrl} using mode=${mode}${mode === "ollama" ? ` model=${model}` : ""}.`);

      const response = await fetch(`${serviceUrl}/intent/patch-model?${query.toString()}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          type: "patch_model",
          current_model: latestBridgeModel,
          prompt: elements.patchPromptInput.value,
        }),
      });
      patchResponse = await response.json();
      logEvent(`Patch service responded with status ${response.status}.`);
      if (!response.ok) {
        throw new Error(patchResponse.error || "The patch request failed.");
      }
      patchResponse.summary = [
        `Generated ${patchResponse.patches.length} patch operation(s).`,
        `Affected views: ${(patchResponse.affected_views || []).join(", ") || "none"}.`,
      ];
    }

    const nextModel = applyPatchLocally(latestBridgeModel, patchResponse);
    updatePatchSummary(patchResponse.summary || []);
    const drawingPlan = createDrawingPlan(nextModel);
    const instructionBatch = createCadInstructionBatch(nextModel, drawingPlan);
    const svg = renderSvgDocument(instructionBatch);
    updateOutputs(nextModel, instructionBatch, svg);
    const affectedViews = (patchResponse.affected_views || []).join(", ") || "none";
    elements.statusText.textContent = `Patch applied. Affected views: ${affectedViews}.`;
    logEvent(`Patch applied. Affected views: ${affectedViews}.`);
  } catch (error) {
    elements.statusText.textContent = error.message;
    logEvent(`Patch request failed: ${error.message}`);
  } finally {
    setBusy(false, "", ["applyPatchButton", "samplePatchButton"]);
  }
}

function downloadText(filename, content, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

function updateSelectedDrawingsFromControls() {
  const nextDrawings = ["general_arrangement"];
  if (elements.drawingPlan.checked) {
    nextDrawings.push("plan");
  }
  if (elements.drawingElevation.checked) {
    nextDrawings.push("elevation");
  }
  if (elements.drawingSection.checked) {
    nextDrawings.push("typical_section");
  }

  if (nextDrawings.length === 1) {
    elements.statusText.textContent = "At least one drawable view is required, so the previous selection was kept.";
    syncDrawingControls();
    return;
  }

  selectedDrawings = nextDrawings;
  syncDrawingControls();
  regenerate();
}

elements.girderDepthPolicy.addEventListener("change", () => {
  syncDepthField();
  regenerate();
});

[
  elements.drawingPlan,
  elements.drawingElevation,
  elements.drawingSection,
].forEach((element) => {
  element.addEventListener("change", updateSelectedDrawingsFromControls);
});

[
  elements.projectId,
  elements.startStation,
  elements.spans,
  elements.deckWidth,
  elements.sectionType,
  elements.pierType,
  elements.abutmentType,
  elements.girderDepth,
].forEach((element) => {
  element.addEventListener("change", regenerate);
});

elements.regenerateButton.addEventListener("click", regenerate);
elements.parsePromptButton.addEventListener("click", () => {
  parsePromptIntoForm();
});
elements.applyPatchButton.addEventListener("click", () => {
  applyPatchPrompt();
});
elements.samplePromptButton.addEventListener("click", () => {
  samplePromptIndex = (samplePromptIndex + 1) % samplePrompts.length;
  elements.promptInput.value = samplePrompts[samplePromptIndex];
  parsePromptIntoForm();
});
elements.samplePatchButton.addEventListener("click", () => {
  samplePatchIndex = (samplePatchIndex + 1) % samplePatches.length;
  elements.patchPromptInput.value = samplePatches[samplePatchIndex];
});
elements.resetButton.addEventListener("click", () => {
  samplePromptIndex = 0;
  samplePatchIndex = 0;
  applyDefaultState();
  updateAssumptions([
    "Bridge type is assumed to be a prestressed continuous girder bridge.",
    "Use the prompt box to draft a new parameter set.",
  ]);
  updatePatchSummary([
    "Apply a follow-up edit after the first model is generated.",
  ]);
  regenerate();
});
elements.downloadSvgButton.addEventListener("click", () => {
  downloadText("vibedraw-preview.svg", latestSvg, "image/svg+xml");
});
elements.downloadModelButton.addEventListener("click", () => {
  downloadText("vibedraw-bridge-model.json", JSON.stringify(latestBridgeModel, null, 2), "application/json");
});

applyDefaultState();
updateAssumptions([
  "Bridge type is assumed to be a prestressed continuous girder bridge.",
  "Use the prompt box to draft a new parameter set.",
]);
updatePatchSummary([
  "Apply a follow-up edit after the first model is generated.",
]);
logEvent("Preview page initialized.");
regenerate();
