export interface Environment {
    GATEWAY_ENDPOINT: string
}

export let ENV: Environment = {
    GATEWAY_ENDPOINT: ""
}

export function set_environment(e: Environment) {
    ENV = e
}