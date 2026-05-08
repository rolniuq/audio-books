# Tiltfile for AudioBook App
# Usage: tilt up (starts all services)
# Stop: tilt down

# Enable live updates for faster development
default_registry('gcr.io/your-project')  # Optional: change to your registry

# Method 1: Use existing docker-compose.yml (simplest)
docker_compose('./docker-compose.yml')

# Configure resources with port forwards
k8s_resource('backend', port_forwards=['8000:8000'])
k8s_resource('frontend', port_forwards=['3000:3000'])

# Method 2: Direct Docker builds with live updates (alternative)
# Uncomment below and comment out docker_compose line above if you prefer this method

# docker_build(
#     'audiobook-backend',
#     './backend',
#     dockerfile='./backend/Dockerfile',
#     live_update=[
#         sync('./backend/app', '/app/app'),
#         sync('./backend/requirements.txt', '/app/requirements.txt'),
#     ]
# )
# 
# docker_build(
#     'audiobook-frontend',
#     './frontend',
#     dockerfile='./frontend/Dockerfile',
#     live_update=[
#         sync('./frontend/src', '/app/src'),
#         sync('./frontend/package.json', '/app/package.json'),
#     ]
# )
# 
# k8s_yaml('./docker-compose.yml')

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
