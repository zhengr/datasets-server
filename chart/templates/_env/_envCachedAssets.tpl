# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 The HuggingFace Authors.

{{- define "envCachedAssets" -}}
- name: CACHED_ASSETS_BASE_URL
  value: "{{ include "cachedAssets.baseUrl" . }}"
- name: CACHED_ASSETS_STORAGE_DIRECTORY
  value: {{ .Values.cachedAssets.storageDirectory | quote }}
- name: CACHED_ASSETS_S3_FOLDER_NAME
  value: {{ .Values.cachedAssets.s3FolderName | quote }}
{{- end -}}
