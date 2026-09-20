export interface EraTheme {
  era: string;
  label: string;
  arabicLabel: string;
  range: string;
  accent: string;
  accentSoft: string;
  onAccent: string;
  glow: string;
  surface: string;
  background: string;
  image: string;
  motif: string;
  scene: string;
  motto: string;
}

// Curated presentation metadata for the "Time Travel" timeline. Order and
// date ranges are for display only — actual retrieval filtering uses
// whatever era strings the backend returns from metadata.csv.
export const ERA_THEMES: EraTheme[] = [
  {
    era: "Ancient Egypt",
    label: "Ancient",
    arabicLabel: "مصر القديمة",
    range: "c. 3100 BCE – 332 BCE",
    accent: "#c9973f",
    accentSoft: "#f2dfb9",
    onAccent: "#2a1c05",
    glow: "rgba(214, 165, 72, 0.32)",
    surface: "rgba(37, 25, 12, 0.72)",
    background: "radial-gradient(circle at 78% 25%, rgba(225, 177, 85, .24), transparent 32%), linear-gradient(125deg, #0c0a08 0%, #24180c 48%, #5a3a16 100%)",
    image: "/eras/ancient.webp",
    motif: "𓂀",
    scene: "Pyramids · Nile · Royal dynasties",
    motto: "Where the Nile shaped a civilization",
  },
  {
    era: "Greco Roman Egypt",
    label: "Greco-Roman",
    arabicLabel: "اليونانية الرومانية",
    range: "332 BCE – 641 CE",
    accent: "#2c5f8a",
    accentSoft: "#dbe9f4",
    onAccent: "#0d1f2d",
    glow: "rgba(100, 174, 218, 0.28)",
    surface: "rgba(18, 30, 43, 0.72)",
    background: "radial-gradient(circle at 78% 22%, rgba(157, 202, 226, .24), transparent 31%), linear-gradient(125deg, #080d13 0%, #142c42 50%, #476c82 100%)",
    image: "/eras/greco-roman.webp",
    motif: "Ω",
    scene: "Alexandria · Marble · Mediterranean light",
    motto: "Alexandria, where worlds and ideas met",
  },
  {
    era: "Coptic Egypt",
    label: "Coptic",
    arabicLabel: "مصر القبطية",
    range: "c. 42 – 641 CE",
    accent: "#7a2e2e",
    accentSoft: "#f1dcdc",
    onAccent: "#2a0e0e",
    glow: "rgba(193, 110, 91, 0.25)",
    surface: "rgba(43, 20, 25, 0.72)",
    background: "radial-gradient(circle at 78% 24%, rgba(211, 143, 112, .22), transparent 30%), linear-gradient(125deg, #100a0c 0%, #321820 50%, #6a3a38 100%)",
    image: "/eras/coptic.webp",
    motif: "✥",
    scene: "Coptic art · Desert monasteries · Warm light",
    motto: "Faith, scholarship, and life in the desert",
  },
  {
    era: "Islamic Egypt",
    label: "Islamic",
    arabicLabel: "مصر الإسلامية",
    range: "641 – 1517 CE",
    accent: "#a9853f",
    accentSoft: "#e8ddbf",
    onAccent: "#211804",
    glow: "rgba(183, 145, 72, 0.28)",
    surface: "rgba(25, 29, 19, 0.74)",
    background: "radial-gradient(circle at 76% 23%, rgba(185, 150, 82, .23), transparent 31%), linear-gradient(125deg, #090b08 0%, #20271a 52%, #554a25 100%)",
    image: "/eras/islamic.webp",
    motif: "۞",
    scene: "Cairo · Citadels · Geometry and calligraphy",
    motto: "Cairo rises at the heart of the age",
  },
  {
    era: "Modern Egypt",
    label: "Modern",
    arabicLabel: "مصر الحديثة",
    range: "1517 – 1952 CE",
    accent: "#b5964b",
    accentSoft: "#eee4c9",
    onAccent: "#201805",
    glow: "rgba(169, 148, 79, 0.26)",
    surface: "rgba(13, 31, 39, 0.74)",
    background: "radial-gradient(circle at 78% 23%, rgba(200, 173, 94, .2), transparent 32%), linear-gradient(125deg, #071014 0%, #123342 52%, #315549 100%)",
    image: "/eras/modern.webp",
    motif: "⚓",
    scene: "Citadel · Nile · State-building and industry",
    motto: "A nation remade through reform and industry",
  },
  {
    era: "Contemporary Egypt",
    label: "Contemporary",
    arabicLabel: "مصر المعاصرة",
    range: "1952 CE – present",
    accent: "#a3312b",
    accentSoft: "#f5dcda",
    onAccent: "#2c0d0b",
    glow: "rgba(204, 84, 63, 0.24)",
    surface: "rgba(26, 29, 25, 0.75)",
    background: "radial-gradient(circle at 77% 25%, rgba(204, 132, 77, .2), transparent 31%), linear-gradient(125deg, #0a0c0b 0%, #2b3027 50%, #665038 100%)",
    image: "/eras/contemporary.webp",
    motif: "✦",
    scene: "Suez Canal · October victory · A changing nation",
    motto: "Memory, resilience, and a changing nation",
  },
];

const DEFAULT_THEME: EraTheme = {
  era: "",
  label: "All Eras",
  arabicLabel: "كل العصور",
  range: "",
  accent: "#3f6b8f",
  accentSoft: "#e2eaf1",
  onAccent: "#101820",
  glow: "rgba(69, 135, 184, 0.26)",
  surface: "rgba(14, 24, 34, 0.72)",
  background: "radial-gradient(circle at 78% 22%, rgba(73, 143, 191, .2), transparent 31%), linear-gradient(125deg, #070b0f 0%, #102537 52%, #233f55 100%)",
  image: "/eras/ancient.webp",
  motif: "⌛",
  scene: "Six eras · One journey through Egyptian history",
  motto: "Six eras, one continuing Egyptian story",
};

export function getEraTheme(era: string | null): EraTheme {
  if (!era) return DEFAULT_THEME;
  return ERA_THEMES.find((theme) => theme.era === era) ?? { ...DEFAULT_THEME, era, label: era };
}

export function orderEras(known: string[]): EraTheme[] {
  if (known.length === 0) return ERA_THEMES;
  const themed = ERA_THEMES.filter((theme) => known.includes(theme.era));
  const extras = known
    .filter((era) => !ERA_THEMES.some((theme) => theme.era === era))
    .map((era) => ({ ...DEFAULT_THEME, era, label: era }));
  return [...themed, ...extras];
}
