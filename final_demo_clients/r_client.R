# MetaPython R Client (Generated)
library(httr)
library(jsonlite)

MetaPythonClient <- function(base_url = "http://localhost:8080") {
  list(
    base_url = base_url,
    run_meta_analysis = function(config) {
      response <- POST(
        paste0(base_url, "/api/v1/analyze"),
        body = toJSON(config, auto_unbox = TRUE),
        content_type_json()
      )
      fromJSON(content(response, "text"))
    }
  )
}
