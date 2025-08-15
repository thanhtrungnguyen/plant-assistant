import { NextResponse, type NextRequest } from "next/server";

// Protect routes that require authentication
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - login, register, forgot-password, reset-password (auth pages)
     */
    "/((?!api|_next/static|_next/image|favicon.ico|login|register|forgot-password|reset-password).*)",
  ],
};

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;

  // Allow auth pages & public routes explicitly
  if (
    pathname.startsWith("/login") ||
    pathname.startsWith("/register") ||
    pathname.startsWith("/forgot-password") ||
    pathname.startsWith("/reset-password") ||
    pathname === "/"
  ) {
    return NextResponse.next();
  }

  // Check for access_token cookie presence
  const access = req.cookies.get("access_token")?.value;

  if (!access) {
    console.log(`🔒 Middleware: No access token found for ${pathname}, redirecting to login`);
    const url = req.nextUrl.clone();
    url.pathname = "/login";
    url.searchParams.set("next", pathname);
    return NextResponse.redirect(url);
  }

  console.log(`✅ Middleware: Access token found for ${pathname}, allowing request`);
  return NextResponse.next();
}
