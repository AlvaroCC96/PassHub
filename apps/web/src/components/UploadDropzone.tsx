import { useRef, useState, type DragEvent } from "react";

interface UploadDropzoneProps {
  file: File | null;
  onFileSelected: (file: File) => void;
  accept?: string;
}

const ACCEPTED_EXTENSIONS = ".pdf,.jpg,.jpeg,.png,.webp";

export function UploadDropzone({ file, onFileSelected, accept = ACCEPTED_EXTENSIONS }: UploadDropzoneProps) {
  const [isDraggingOver, setIsDraggingOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDraggingOver(false);
    const dropped = event.dataTransfer.files[0];
    if (dropped) onFileSelected(dropped);
  };

  return (
    <div
      onDragOver={(event) => {
        event.preventDefault();
        setIsDraggingOver(true);
      }}
      onDragLeave={() => setIsDraggingOver(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
      role="button"
      tabIndex={0}
      className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-10 text-center transition-colors ${
        isDraggingOver
          ? "border-brand-500 bg-brand-50 dark:bg-brand-600/10"
          : "border-slate-300 hover:border-brand-400 dark:border-slate-700"
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        className="hidden"
        onChange={(event) => {
          const selected = event.target.files?.[0];
          if (selected) onFileSelected(selected);
        }}
      />
      <span className="text-3xl" aria-hidden="true">
        📎
      </span>
      {file ? (
        <p className="mt-2 text-sm font-medium">{file.name}</p>
      ) : (
        <>
          <p className="mt-2 text-sm font-medium">Drag and drop a file, or click to browse</p>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            PDF, JPG, PNG, or WEBP — up to 10MB
          </p>
        </>
      )}
    </div>
  );
}
