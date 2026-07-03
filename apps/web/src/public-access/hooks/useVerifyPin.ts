import { useMutation } from "@tanstack/react-query";
import { fetchVerifyPin } from "../api";
import type { VerifyPinResponse } from "../types";

export function useVerifyPin(publicToken: string) {
  return useMutation<VerifyPinResponse, Error, string>({
    mutationFn: (pin: string) => fetchVerifyPin(publicToken, pin),
    retry: false,
  });
}
