import { post } from "./api";

export async function loginAdmin(mobile: string, otp: string) {
  await post("/auth/otp/request", { mobile_e164: mobile, purpose: "LOGIN" });
  const token = await post<any>("/auth/otp/verify", {
    mobile_e164: mobile,
    otp,
    purpose: "LOGIN"
  });
  localStorage.setItem("access_token", token.access_token);
  localStorage.setItem("refresh_token", token.refresh_token);
}
