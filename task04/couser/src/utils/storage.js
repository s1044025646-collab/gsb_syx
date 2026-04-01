const KEY_FILES = "medfl-local-files-v1";
const KEY_PRIVACY = "medfl-privacy-v1";
const KEY_TASK_APPLY = "medfl-task-apply-v1";

const seedFiles = [
  {
    id: "f1",
    name: "lung_ct_batch_2025Q1.parquet",
    sizeBytes: 1284000000,
    uploadedAt: "2025-12-18T09:30:00",
    featureCount: 512,
  },
  {
    id: "f2",
    name: "derm_images_manifest.csv",
    sizeBytes: 2400000,
    uploadedAt: "2025-12-20T14:12:00",
    featureCount: 48,
  },
];

function safeParse(json, fallback) {
  try {
    return JSON.parse(json) ?? fallback;
  } catch {
    return fallback;
  }
}

export function getLocalFiles() {
  const raw = localStorage.getItem(KEY_FILES);
  if (!raw) {
    localStorage.setItem(KEY_FILES, JSON.stringify(seedFiles));
    return [...seedFiles];
  }
  const arr = safeParse(raw, []);
  return Array.isArray(arr) && arr.length ? arr : [...seedFiles];
}

export function setLocalFiles(files) {
  localStorage.setItem(KEY_FILES, JSON.stringify(files));
  window.dispatchEvent(new Event("medfl-storage"));
}

export function addLocalFileMeta({ name, sizeBytes, featureCount }) {
  const files = getLocalFiles();
  setLocalFiles(
    files
      .slice()
      .concat([
        {
          id: `f-${Date.now()}`,
          name,
          sizeBytes,
          uploadedAt: new Date().toISOString(),
          featureCount: featureCount ?? 0,
        },
      ]) && files
  );
}

export function getPrivacySettings() {
  const raw = localStorage.getItem(KEY_PRIVACY);
  const d = { hideName: false, blurBirth: false, dpNoise: false };
  return { ...d, ...safeParse(raw, {}) };
}

export function setPrivacySettings(s) {
  localStorage.setItem(KEY_PRIVACY, JSON.stringify(s));
  window.dispatchEvent(new Event("medfl-storage"));
}

export function getTaskApplications() {
  return safeParse(localStorage.getItem(KEY_TASK_APPLY), {});
}

export function setTaskApplication(taskId, mapping) {
  const all = getTaskApplications();
  all[taskId] = { mapping, at: new Date().toISOString() };
  localStorage.setItem(KEY_TASK_APPLY, JSON.stringify(all));
  window.dispatchEvent(new Event("medfl-storage"));
}

export function totalDataBytes() {
  const files = getLocalFiles();
  const sum = files.reduce((s, f) => s + (f.sizeBytes || 0), 0);
  if (files.length === 0) return sum;
  return sum + (files[files.length - 1].sizeBytes || 0);
}
