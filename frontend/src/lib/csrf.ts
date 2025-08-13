export function getCookie(name: string): string | undefined {
  if (typeof document === "undefined") return undefined;
  return `; ${document.cookie}`.split(`; ${name}=`).pop()?.split(";").shift();
}

export function getCsrf(): string | undefined {
  return getCookie("csrf_token");
}
