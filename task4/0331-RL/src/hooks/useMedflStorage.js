import { useEffect, useState } from "react";
import {
  getLocalFiles,
  getPrivacySettings,
  getTaskApplications,
} from "../utils/storage";

const EVT = "medfl-storage";

export function useLocalFiles() {
  const [files, setFiles] = useState(() => getLocalFiles());
  useEffect(() => {
    const on = () => setFiles(getLocalFiles());
    window.addEventListener(EVT, on);
    return () => window.removeEventListener(EVT, on);
  }, []);
  return files;
}

export function useDataPageState() {
  const [state, setState] = useState(() => ({
    files: getLocalFiles(),
    privacy: getPrivacySettings(),
  }));
  useEffect(() => {
    const on = () =>
      setState({
        files: getLocalFiles(),
        privacy: getPrivacySettings(),
      });
    window.addEventListener(EVT, on);
    return () => window.removeEventListener(EVT, on);
  }, []);
  return state;
}

export function useTaskApplicationsMap() {
  const [map, setMap] = useState(() => getTaskApplications());
  useEffect(() => {
    const on = () => setMap(getTaskApplications());
    window.addEventListener(EVT, on);
    return () => window.removeEventListener(EVT, on);
  }, []);
  return map;
}
