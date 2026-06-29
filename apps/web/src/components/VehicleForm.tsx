import { FuelType, Transmission, type VehicleInput } from "@passhub/shared";
import { Button } from "@passhub/ui";
import { useState, type FormEvent, type ReactNode } from "react";

interface VehicleFormProps {
  initialValues?: VehicleInput;
  onSubmit: (values: VehicleInput) => void;
  isSubmitting: boolean;
  submitLabel: string;
  errorMessage?: string | null;
}

const FUEL_LABELS: Record<FuelType, string> = {
  [FuelType.Gasoline]: "Gasoline",
  [FuelType.Diesel]: "Diesel",
  [FuelType.Hybrid]: "Hybrid",
  [FuelType.Electric]: "Electric",
  [FuelType.Unknown]: "Unknown",
};

const TRANSMISSION_LABELS: Record<Transmission, string> = {
  [Transmission.Manual]: "Manual",
  [Transmission.Automatic]: "Automatic",
  [Transmission.Cvt]: "CVT",
  [Transmission.Unknown]: "Unknown",
};

const EMPTY_VALUES: VehicleInput = {
  plate: "",
  brand: "",
  model: "",
  year: new Date().getFullYear(),
  color: "",
  vin: "",
  engine_number: "",
  nickname: "",
  fuel_type: FuelType.Unknown,
  transmission: Transmission.Unknown,
};

export function VehicleForm({
  initialValues,
  onSubmit,
  isSubmitting,
  submitLabel,
  errorMessage,
}: VehicleFormProps) {
  const [values, setValues] = useState<VehicleInput>(initialValues ?? EMPTY_VALUES);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  const update = <K extends keyof VehicleInput>(key: K, value: VehicleInput[K]) => {
    setValues((prev) => ({ ...prev, [key]: value }));
  };

  const validate = (): boolean => {
    const errors: Record<string, string> = {};
    if (!values.plate.trim()) errors.plate = "Plate is required";
    if (!values.brand.trim()) errors.brand = "Brand is required";
    if (!values.model.trim()) errors.model = "Model is required";
    const nextYear = new Date().getFullYear() + 1;
    if (!values.year || values.year < 1900 || values.year > nextYear) {
      errors.year = `Year must be between 1900 and ${nextYear}`;
    }
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (validate()) onSubmit(values);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {errorMessage && (
        <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-500/10 dark:text-red-400">
          {errorMessage}
        </p>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Field label="Plate" error={fieldErrors.plate}>
          <input
            value={values.plate}
            onChange={(e) => update("plate", e.target.value)}
            className={inputClass(Boolean(fieldErrors.plate))}
          />
        </Field>
        <Field label="Brand" error={fieldErrors.brand}>
          <input
            value={values.brand}
            onChange={(e) => update("brand", e.target.value)}
            className={inputClass(Boolean(fieldErrors.brand))}
          />
        </Field>
        <Field label="Model" error={fieldErrors.model}>
          <input
            value={values.model}
            onChange={(e) => update("model", e.target.value)}
            className={inputClass(Boolean(fieldErrors.model))}
          />
        </Field>
        <Field label="Year" error={fieldErrors.year}>
          <input
            type="number"
            value={values.year}
            onChange={(e) => update("year", Number(e.target.value))}
            className={inputClass(Boolean(fieldErrors.year))}
          />
        </Field>
        <Field label="Color">
          <input
            value={values.color ?? ""}
            onChange={(e) => update("color", e.target.value)}
            className={inputClass(false)}
          />
        </Field>
        <Field label="VIN">
          <input
            value={values.vin ?? ""}
            onChange={(e) => update("vin", e.target.value)}
            className={inputClass(false)}
          />
        </Field>
        <Field label="Engine number">
          <input
            value={values.engine_number ?? ""}
            onChange={(e) => update("engine_number", e.target.value)}
            className={inputClass(false)}
          />
        </Field>
        <Field label="Nickname">
          <input
            value={values.nickname ?? ""}
            onChange={(e) => update("nickname", e.target.value)}
            className={inputClass(false)}
          />
        </Field>
        <Field label="Fuel type">
          <select
            value={values.fuel_type}
            onChange={(e) => update("fuel_type", e.target.value as FuelType)}
            className={inputClass(false)}
          >
            {Object.values(FuelType).map((value) => (
              <option key={value} value={value}>
                {FUEL_LABELS[value]}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Transmission">
          <select
            value={values.transmission}
            onChange={(e) => update("transmission", e.target.value as Transmission)}
            className={inputClass(false)}
          >
            {Object.values(Transmission).map((value) => (
              <option key={value} value={value}>
                {TRANSMISSION_LABELS[value]}
              </option>
            ))}
          </select>
        </Field>
      </div>

      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Saving…" : submitLabel}
      </Button>
    </form>
  );
}

function inputClass(hasError: boolean): string {
  return `w-full rounded-md border px-3 py-2 text-sm dark:bg-slate-800 ${
    hasError ? "border-red-400" : "border-slate-300 dark:border-slate-700"
  }`;
}

function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: ReactNode;
}) {
  return (
    <label className="flex flex-col gap-1 text-sm">
      <span className="font-medium">{label}</span>
      {children}
      {error && <span className="text-xs text-red-600 dark:text-red-400">{error}</span>}
    </label>
  );
}
