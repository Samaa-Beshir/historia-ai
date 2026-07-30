export interface EraTheme {
  era: string;
  label: string;
  range: string;
  accent: string;
  accentSoft: string;
  onAccent: string;
}

// Curated presentation metadata for the "Time Travel" timeline. Order and
// date ranges are for display only — actual retrieval filtering uses
// whatever era strings the backend returns from metadata.csv.
export const ERA_THEMES: EraTheme[] = [
  {
    era: "Ancient Egypt",
    label: "Ancient",
    range: "c. 3100 BCE – 332 BCE",
    accent: "#b8862b",
    accentSoft: "#f4e6c8",
    onAccent: "#2a1c05",
  },
  {
    era: "Greco Roman Egypt",
    label: "Greco-Roman",
    range: "332 BCE – 641 CE",
    accent: "#2c5f8a",
    accentSoft: "#dbe9f4",
    onAccent: "#0d1f2d",
  },
  {
    era: "Coptic Egypt",
    label: "Coptic",
    range: "c. 42 – 641 CE",
    accent: "#7a2e2e",
    accentSoft: "#f1dcdc",
    onAccent: "#2a0e0e",
  },
  {
    era: "Islamic Egypt",
    label: "Islamic",
    range: "641 – 1517 CE",
    accent: "#1f7a5c",
    accentSoft: "#d9efe6",
    onAccent: "#07211a",
  },
  {
    era: "Modern Egypt",
    label: "Modern",
    range: "1517 – 1952 CE",
    accent: "#4b3f8a",
    accentSoft: "#e3dff4",
    onAccent: "#1a1530",
  },
  {
    era: "Contemporary Egypt",
    label: "Contemporary",
    range: "1952 CE – present",
    accent: "#a3312b",
    accentSoft: "#f5dcda",
    onAccent: "#2c0d0b",
  },
];

const DEFAULT_THEME: EraTheme = {
  era: "",
  label: "All Eras",
  range: "",
  accent: "#3f6b8f",
  accentSoft: "#e2eaf1",
  onAccent: "#101820",
};

export function getEraTheme(era: string | null): EraTheme {
  if (!era) return DEFAULT_THEME;
  return ERA_THEMES.find((theme) => theme.era === era) ?? { ...DEFAULT_THEME, era, label: era };
}

export function orderEras(known: string[]): EraTheme[] {
  const themed = ERA_THEMES.filter((theme) => known.includes(theme.era));
  const extras = known
    .filter((era) => !ERA_THEMES.some((theme) => theme.era === era))
    .map((era) => ({ ...DEFAULT_THEME, era, label: era }));
  return [...themed, ...extras];
}
