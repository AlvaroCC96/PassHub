import type { FuelType } from "./fuel-type";
import type { Transmission } from "./transmission";
import type { VehicleStatus } from "./vehicle-status";

/** Mirrors `VehicleResponse` returned by `/api/v1/drivepass/vehicles/*`. */
export interface Vehicle {
  id: string;
  plate: string;
  brand: string;
  model: string;
  year: number;
  color: string | null;
  vin: string | null;
  engine_number: string | null;
  nickname: string | null;
  fuel_type: FuelType;
  transmission: Transmission;
  favorite: boolean;
  status: VehicleStatus;
}

export interface VehicleInput {
  plate: string;
  brand: string;
  model: string;
  year: number;
  color?: string | null;
  vin?: string | null;
  engine_number?: string | null;
  nickname?: string | null;
  fuel_type?: FuelType;
  transmission?: Transmission;
}
