// Placeholder product name — not finalized yet. Swap this one value once a
// name is chosen instead of hunting through components.
export const APP_NAME = "Contract AI";

export const APP_TAGLINE = "Enterprise Legal AI";

// Upload constraints — PDF only for now (task 845). Keep these two values
// as the single source of truth so the dropzone's validation logic and its
// on-screen copy can never drift apart.
export const ACCEPTED_FILE_EXTENSIONS = [".pdf"] as const;
export const ACCEPTED_FILE_ACCEPT_ATTR = ACCEPTED_FILE_EXTENSIONS.join(",");
export const MAX_FILE_SIZE_MB = 50;
export const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;
