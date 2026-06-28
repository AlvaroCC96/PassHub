/** Mirrors the error envelope produced by `register_exception_handlers` in the API. */
export interface ApiError {
  error: {
    code: string;
    message: string;
    request_id: string | null;
  };
}
