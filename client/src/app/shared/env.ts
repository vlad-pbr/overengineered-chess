export interface Environment {
    GATEWAY_HTTP_ENDPOINT: string
    GATEWAY_WS_ENDPOINT: string
}

export let ENV: Environment = {
    GATEWAY_HTTP_ENDPOINT: "",
    GATEWAY_WS_ENDPOINT: ""
}

export function set_environment(e: Environment) {
    ENV = e
}