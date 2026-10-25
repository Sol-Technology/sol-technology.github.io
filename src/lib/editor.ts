import { basicSetup } from "codemirror";
import { EditorState, type Extension } from "@codemirror/state";
import { EditorView, keymap, placeholder as placeholderExt } from "@codemirror/view";
import { json } from "@codemirror/lang-json";
import { StreamLanguage } from "@codemirror/language";
import { csharp } from "@codemirror/legacy-modes/mode/clike";

export interface Editor {
  get(): string;
  set(value: string): void;
  focus(): void;
}

interface Options {
  language?: "json" | "csharp" | "text";
  value?: string;
  readOnly?: boolean;
  placeholder?: string;
  onChange?: (value: string) => void;
  onRun?: () => void;
  minHeight?: string;
  maxHeight?: string;
}

const theme = (minHeight: string, maxHeight: string) =>
  EditorView.theme({
    "&": { fontSize: "13px", border: "1px solid var(--color-line)", borderRadius: "0.75rem", backgroundColor: "white" },
    "&.cm-focused": { outline: "2px solid color-mix(in srgb, var(--color-sky) 50%, transparent)", outlineOffset: "1px" },
    ".cm-scroller": { fontFamily: "var(--font-mono)", minHeight, maxHeight, overflow: "auto" },
    ".cm-gutters": { backgroundColor: "var(--color-mist)", borderRight: "1px solid var(--color-line)", borderRadius: "0.75rem 0 0 0.75rem" },
    ".cm-content": { paddingBlock: "8px" },
  });

export function createEditor(parent: HTMLElement, options: Options = {}): Editor {
  const extensions: Extension[] = [basicSetup, theme(options.minHeight ?? "16rem", options.maxHeight ?? "32rem"), EditorView.lineWrapping];
  if (options.language === "json") extensions.push(json());
  if (options.language === "csharp") extensions.push(StreamLanguage.define(csharp));
  if (options.readOnly) extensions.push(EditorState.readOnly.of(true));
  if (options.placeholder) extensions.push(placeholderExt(options.placeholder));
  if (options.onRun) {
    const run = options.onRun;
    extensions.push(keymap.of([{ key: "Mod-Enter", run: () => (run(), true) }]));
  }
  if (options.onChange) {
    const onChange = options.onChange;
    extensions.push(EditorView.updateListener.of((update) => update.docChanged && onChange(update.state.doc.toString())));
  }

  const view = new EditorView({ parent, state: EditorState.create({ doc: options.value ?? "", extensions }) });
  return {
    get: () => view.state.doc.toString(),
    set: (value) => view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: value } }),
    focus: () => view.focus(),
  };
}
