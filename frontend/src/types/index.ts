export interface Device {
  id: string;
  name: string;
  model: string;
  type: "cast" | "audio" | "group";
  volume: number; // 0.0 to 1.0
  is_active: boolean;
}
