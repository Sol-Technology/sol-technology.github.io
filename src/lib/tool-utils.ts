// Small helpers shared by the AvroConvert Online pages. Nothing here sends data anywhere.

export const $ = <T extends HTMLElement = HTMLElement>(selector: string, root: ParentNode = document) => root.querySelector<T>(selector)!;

export function debounce<A extends unknown[]>(fn: (...args: A) => void, ms = 300) {
  let timer: ReturnType<typeof setTimeout> | undefined;
  return (...args: A) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), ms);
  };
}

export async function copyText(text: string, button?: HTMLElement) {
  await navigator.clipboard.writeText(text);
  if (button) flash(button, "Copied");
}

export function download(data: Uint8Array | string, fileName: string, type = "application/octet-stream") {
  const blob = new Blob([data as BlobPart], { type });
  const url = URL.createObjectURL(blob);
  const a = Object.assign(document.createElement("a"), { href: url, download: fileName });
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function flash(button: HTMLElement, label: string) {
  const original = button.textContent;
  button.textContent = label;
  setTimeout(() => (button.textContent = original), 1200);
}

export function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
}

/** Shows an error box (or hides it when message is empty). */
export function showError(box: HTMLElement, message?: string) {
  box.hidden = !message;
  box.textContent = message ?? "";
}

// ---- persistence: per visitor, in this browser only ----------------------------------------------------------------

export const stored = {
  get(key: string): string | null {
    try {
      return localStorage.getItem(`avroconvert-online:${key}`);
    } catch {
      return null;
    }
  },
  set(key: string, value: string) {
    try {
      localStorage.setItem(`avroconvert-online:${key}`, value);
    } catch {
      // private mode or storage disabled: the tool works without it
    }
  },
};

// ---- shareable links: the state travels in the URL fragment, which browsers never send to the server ---------------

const toBase64Url = (bytes: Uint8Array) => btoa(String.fromCharCode(...bytes)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
const fromBase64Url = (text: string) => Uint8Array.from(atob(text.replace(/-/g, "+").replace(/_/g, "/")), (c) => c.charCodeAt(0));

async function pipe(bytes: Uint8Array, stream: CompressionStream | DecompressionStream) {
  return new Uint8Array(await new Response(new Blob([bytes as BlobPart]).stream().pipeThrough(stream)).arrayBuffer());
}

export async function shareLink(state: Record<string, string>) {
  const packed = await pipe(new TextEncoder().encode(JSON.stringify(state)), new CompressionStream("deflate-raw"));
  return `${location.origin}${location.pathname}#s=${toBase64Url(packed)}`;
}

export async function sharedState(): Promise<Record<string, string> | null> {
  const match = location.hash.match(/^#s=([\w-]+)$/);
  if (!match) return null;
  try {
    const bytes = await pipe(fromBase64Url(match[1]), new DecompressionStream("deflate-raw"));
    return JSON.parse(new TextDecoder().decode(bytes));
  } catch {
    return null;
  }
}

export function wireShareButton(button: HTMLElement, state: () => Record<string, string>) {
  button.addEventListener("click", async () => {
    const link = await shareLink(state());
    history.replaceState(null, "", link);
    await copyText(link, button);
    flash(button, "Link copied");
  });
}

// ---- binary input ----------------------------------------------------------------------------------------------------

export async function readFile(file: File) {
  return new Uint8Array(await file.arrayBuffer());
}

/** Hex (with or without spaces, 0x, \x) or base64 to bytes. */
export function parseBytes(text: string): Uint8Array {
  const trimmed = text.trim();
  const hex = trimmed.replace(/0x|\\x|[\s,:]/gi, "");
  if (hex.length > 0 && hex.length % 2 === 0 && /^[0-9a-f]+$/i.test(hex)) {
    return Uint8Array.from(hex.match(/../g)!, (h) => parseInt(h, 16));
  }
  try {
    return Uint8Array.from(atob(trimmed.replace(/-/g, "+").replace(/_/g, "/")), (c) => c.charCodeAt(0));
  } catch {
    throw new Error("Paste the message as hex (00 00 00 00 07 …) or base64.");
  }
}

/** Makes an element accept dropped files and a hidden file input open on click. */
export function wireDropZone(zone: HTMLElement, input: HTMLInputElement, onFile: (file: File) => void) {
  zone.addEventListener("click", () => input.click());
  zone.addEventListener("keydown", (e) => (e.key === "Enter" || e.key === " ") && (e.preventDefault(), input.click()));
  input.addEventListener("change", () => input.files?.[0] && onFile(input.files[0]));
  zone.addEventListener("dragover", (e) => {
    e.preventDefault();
    zone.dataset.over = "true";
  });
  zone.addEventListener("dragleave", () => delete zone.dataset.over);
  zone.addEventListener("drop", (e) => {
    e.preventDefault();
    delete zone.dataset.over;
    const file = e.dataTransfer?.files?.[0];
    if (file) onFile(file);
  });
}
