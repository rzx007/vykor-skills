import { fileURLToPath } from "node:url"
import { defineConfig, loadEnv } from "vite"

export default defineConfig(({ command, mode }) => {
  if (command !== "serve") return {}
  const { NOMI_MODEL_ID: model, NOMI_MODEL_BASE_URL: baseUrl, NOMI_MODEL_API_KEY: apiKey } =
    loadEnv(mode, fileURLToPath(new URL(".", import.meta.url)), "NOMI_MODEL_")
  const ready = Boolean(model && baseUrl && apiKey)

  return {
    server: { host: "127.0.0.1", cors: false },
    plugins: [{
      name: "nomi-local-test-model",
      configureServer(server) {
        server.middlewares.use((request, response, next) => {
          const path = request.url
          if (path !== "/__nomi/model" && path !== "/__nomi/model/connection") return next()
          const host = request.headers.host
          const origin = request.headers.origin
          const loopback = ["127.0.0.1", "::ffff:127.0.0.1"].includes(request.socket.remoteAddress ?? "")
          if (request.method !== "GET" || request.headers["x-nomi-starter"] !== "1" ||
              !loopback || !/^127\.0\.0\.1:\d+$/.test(host ?? "") ||
              (origin && origin !== "http://" + host) || request.headers["sec-fetch-site"] === "cross-site") {
            response.writeHead(403).end()
            return
          }
          const value = !ready ? null : path === "/__nomi/model" ? { model } : { baseUrl, apiKey, apiFormat: "openai" }
          response.writeHead(200, { "Content-Type": "application/json", "Cache-Control": "no-store" })
          response.end(JSON.stringify(value))
        })
      },
    }],
  }
})
