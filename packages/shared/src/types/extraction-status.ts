/** Mirrors `ExtractionStatus` in
 * `apps/api/src/modules/intelligence/domain/value_objects/extraction_status.py`. */
export enum ExtractionStatus {
  Pending = "PENDING",
  Processing = "PROCESSING",
  Completed = "COMPLETED",
  Failed = "FAILED",
  Confirmed = "CONFIRMED",
  Rejected = "REJECTED",
}
