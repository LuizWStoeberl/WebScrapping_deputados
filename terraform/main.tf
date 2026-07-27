terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.33"
    }
  }
}


# Provider Google Cloud



provider "google" {
  project = "projeto-transparencia-496822"
  region  = "us-central1"
}



# APIs necessárias



resource "google_project_service" "services" {
  for_each = toset([
    "bigquery.googleapis.com",
    "cloudfunctions.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "storage.googleapis.com"
  ])

  service = each.key

  disable_on_destroy = false
}

# Dataset BigQuery



resource "google_bigquery_dataset" "dados_camara" {
  dataset_id = "dados_camara"
  location   = "US"

  depends_on = [
    google_project_service.services
  ]
}



# Tabela BigQuery



resource "google_bigquery_table" "raw_gastos" {
  dataset_id = google_bigquery_dataset.dados_camara.dataset_id
  table_id   = "raw_gastos"

  deletion_protection = false

  schema = jsonencode([
    {
      name = "id_registro"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "id_deputado"
      type = "INTEGER"
      mode = "REQUIRED"
    },
    {
      name = "nome_deputado"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name = "estado"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name = "ano"
      type = "INTEGER"
      mode = "NULLABLE"
    },
    {
      name = "mes"
      type = "INTEGER"
      mode = "NULLABLE"
    },
    {
      name = "tipo_despesa"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name = "valor"
      type = "FLOAT"
      mode = "NULLABLE"
    }
  ])

  depends_on = [
    google_bigquery_dataset.dados_camara
  ]
}



# Bucket da Cloud Function



resource "google_storage_bucket" "function_bucket" {
  name     = "bucket-functions-camara-123456"
  location = "US"

  uniform_bucket_level_access = true
}



# Upload ZIP



resource "google_storage_bucket_object" "function_zip" {
  name   = "function-source.zip"
  bucket = google_storage_bucket.function_bucket.name
  source = "function-source.zip"
}



# Cloud Function



resource "google_cloudfunctions_function" "api_camara_function" {

  name        = "api-camara-function"
  description = "Coleta despesas da Câmara e envia ao BigQuery"

  runtime = "python311"

  available_memory_mb = 1024
  timeout             = 540

  source_archive_bucket = google_storage_bucket.function_bucket.name
  source_archive_object = google_storage_bucket_object.function_zip.name

  trigger_http = true

  entry_point = "main"

  environment_variables = {
    PROJECT_ID = "projeto-transparencia-496822"
    DATASET_ID = google_bigquery_dataset.dados_camara.dataset_id
    TABLE_ID   = google_bigquery_table.raw_gastos.table_id
  }

  depends_on = [
    google_project_service.services
  ]
}



# Permissão HTTP pública



resource "google_cloudfunctions_function_iam_member" "invoker" {
  project        = google_cloudfunctions_function.api_camara_function.project
  region         = google_cloudfunctions_function.api_camara_function.region
  cloud_function = google_cloudfunctions_function.api_camara_function.name

  role   = "roles/cloudfunctions.invoker"
  member = "allUsers"
}



# Permissão Artifact Registry



resource "google_project_iam_member" "artifact_registry_reader" {

  project = "projeto-transparencia-496822"

  role = "roles/artifactregistry.reader"

  member = "serviceAccount:service-1067506642404@gcf-admin-robot.iam.gserviceaccount.com"
}
