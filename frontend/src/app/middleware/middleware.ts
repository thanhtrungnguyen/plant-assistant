import { NextResponse, type NextRequest } from "next/server";

// Protect everything under /(app)
export const config = {
  matcher: ["/((app)/:path*)"],
};

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;

  // Allow auth pages & public routes
  if (
    pathname.startsWith("/login") ||
    pathname.startsWith("/register") ||
    pathname.startsWith("/forgot-password") ||
    pathname.startsWith("/reset-password")
  ) {
    return NextResponse.next();
  }

  // Check for access_token cookie presence (quick gate). If absent, send to login.
  const access = req.cookies.get("access_token")?.value;
  if (!access && pathname.startsWith("/")) {
    const url = req.nextUrl.clone();
    url.pathname = "/login";
    url.searchParams.set("next", pathname);
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}
