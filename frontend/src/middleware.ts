import { NextResponse, type NextRequest } from "next/server";

const protectedRoutes = ["/dashboard", "/companies", "/customers", "/products", "/dte", "/settings", "/subscription", "/api-keys", "/onboarding", "/superadmin"];

export function middleware(request: NextRequest) {
  const cookieName = process.env.NEXT_PUBLIC_AUTH_COOKIE_NAME ?? "hme_fact_token";
  const token = request.cookies.get(cookieName) || request.cookies.get("hme_fact_token") || request.cookies.get("ohmefact_token") || request.cookies.get("access_token");
  const isProtected = protectedRoutes.some((route) => request.nextUrl.pathname.startsWith(route));

  if (isProtected && !token) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", request.nextUrl.pathname);
    return NextResponse.redirect(loginUrl);
  }

  if (request.nextUrl.pathname === "/login" && token) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"]
};
