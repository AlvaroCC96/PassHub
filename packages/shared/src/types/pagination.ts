export interface PagedResult<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}
