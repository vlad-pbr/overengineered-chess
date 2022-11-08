export interface Coordinate {
    x: number
    y: number
}

export function is_coordinate_equal(c1: Coordinate, c2: Coordinate): boolean {
    return c1.x == c2.x && c1.y == c2.y
}

export function is_coordinate_in(c: Coordinate, l: Coordinate[]): boolean {
    return l.some((lc) => is_coordinate_equal(c, lc))
}