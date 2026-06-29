/** Mirrors `DocumentType` in `apps/api/src/modules/drivepass/documents/domain/value_objects/document_type.py`. */
export enum DocumentType {
  Padron = "PADRON",
  Soap = "SOAP",
  RevisionTecnica = "REVISION_TECNICA",
  CertificadoGases = "CERTIFICADO_GASES",
  CertificadoHomologacion = "CERTIFICADO_HOMOLOGACION",
  PermisoCirculacion = "PERMISO_CIRCULACION",
  SeguroParticular = "SEGURO_PARTICULAR",
  LicenciaConducir = "LICENCIA_CONDUCIR",
}

/** Only these are accepted by the vehicle document endpoints — mirrors
 * `VEHICLE_DOCUMENT_TYPES` (LICENCIA_CONDUCIR belongs to a user, not a vehicle). */
export const VEHICLE_DOCUMENT_TYPES: DocumentType[] = [
  DocumentType.Padron,
  DocumentType.Soap,
  DocumentType.RevisionTecnica,
  DocumentType.CertificadoGases,
  DocumentType.CertificadoHomologacion,
  DocumentType.PermisoCirculacion,
  DocumentType.SeguroParticular,
];

export const DOCUMENT_TYPE_LABELS: Record<DocumentType, string> = {
  [DocumentType.Padron]: "Padrón",
  [DocumentType.Soap]: "SOAP",
  [DocumentType.RevisionTecnica]: "Revisión Técnica",
  [DocumentType.CertificadoGases]: "Certificado de Gases",
  [DocumentType.CertificadoHomologacion]: "Certificado de Homologación",
  [DocumentType.PermisoCirculacion]: "Permiso de Circulación",
  [DocumentType.SeguroParticular]: "Seguro Particular",
  [DocumentType.LicenciaConducir]: "Licencia de Conducir",
};
