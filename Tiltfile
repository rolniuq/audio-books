# Tiltfile for AudioBook App
# Usage: tilt up (starts all services)
# Stop: tilt down

# Use docker-compose (simplest - one command setup)
docker_compose('./docker-compose.yml')

# Note: default_registry() is NOT used here as it's incompatible with docker_compose()

# docker-compose automatically handles port forwarding
# Backend will be available at http://localhost:8000
# Frontend will be available at http://localhost:3000

# Print helpful information
print('🎧 AudioBook App - Tilt Setup')
print('================================')
print('Backend API: http://localhost:8000')
print('API Docs: http://localhost:8000/docs')
print('Frontend: http://localhost:3000')
print('================================')
print('')
print('To stop: tilt down')
print('To view logs: tilt get k8sresource')
