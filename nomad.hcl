job "overseerr-sync" {
  datacenters = ["hetzner"]

  type = "batch"

  periodic {
    cron = "*/10 * * * *"
    prohibit_overlap = true
  }

  reschedule {
    attempts = 0
  }

  group "app" {
    count = 1

    task "budofit" {
      driver = "docker"

      config {
        image      = "ghcr.io/lostb1t/overseerrsync:latest"
        force_pull = true
        ports      = ["http"]
        auth {
          username = meta.GITHUB_USERNAME
          password = meta.GITHUB_TOKEN
        }
      }

      env {
        DJANGO_SETTINGS_MODULE = "settings.prod"
      }

      resources {
        cpu    = 250
        memory = 125
        memory_max = 500
      }

      volume_mount {
        volume      = "local"
        destination = "/data"
        read_only   = false
      }
    }
  }
}
