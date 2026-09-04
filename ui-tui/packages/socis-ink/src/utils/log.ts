export function logError(error: unknown): void {
  if (!process.env.SOCIS_AGENT_INK_DEBUG_ERRORS) {
    return
  }

  console.error(error)
}
