import CoreLocation
import Foundation

// Sends a user prompt to a third-party AI service.
let aiEndpoint = "https://api.openai.com/v1/chat/completions"

final class LocationClient {
    let manager = CLLocationManager()
    func start() { manager.requestWhenInUseAuthorization() }
}
