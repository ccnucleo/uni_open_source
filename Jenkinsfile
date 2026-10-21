pipeline {
    agent any

    options {
        timeout(time: 60, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '30'))
        disableConcurrentBuilds()
    }

    parameters {
        choice(
            name: 'SYNC_TARGET',
            choices: [
                'all',
                'courses',
                'jobs'
            ],
            description: 'Objetivo de sincronización: cursos, vacantes de empleo o ambos'
        )
        choice(
            name: 'SOURCE',
            choices: [
                'all',
                'microsoft_learn',
                'google_skills',
                'kaggle',
                'huggingface',
                'hubspot',
                'talento_digital_pcm',
                'the_odin_project',
                'freecodecamp',
                'mit_ocw'
            ],
            description: 'Plataforma específica de CURSOS a sincronizar (o "all")'
        )
        choice(
            name: 'GROUP',
            choices: [
                'all_groups',
                'ai',
                'cloud',
                'industrial',
                'software',
                'peru',
                'general'
            ],
            description: 'Filtrar CURSOS por grupo temático'
        )
        choice(
            name: 'JOB_SOURCE',
            choices: [
                'all',
                'getonbrd',
                'remoteok',
                'empleos_peru',
                'computrabajo'
            ],
            description: 'Portal específico de EMPLEOS a sincronizar (o "all")'
        )
        choice(
            name: 'JOB_GROUP',
            choices: [
                'all_groups',
                'tech',
                'peru',
                'remote'
            ],
            description: 'Filtrar EMPLEOS por grupo temático'
        )
        booleanParam(
            name: 'DRY_RUN',
            defaultValue: false,
            description: 'Simular la sincronización sin guardar cambios en la base de datos de Supabase'
        )
        string(
            name: 'LIMIT',
            defaultValue: '',
            description: 'Límite máximo por conector (dejar vacío para procesar todos)'
        )
    }

    triggers {
        // Ejecución automática programada todos los días a las 03:00 AM hora local
        cron('H 3 * * *')
    }

    environment {
        PYTHONUNBUFFERED = '1'
    }

    stages {
        stage('Preparar Entorno Virtual') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            python3 -m venv .venv || true
                            . .venv/bin/activate
                            pip install --upgrade pip
                            pip install -r requirements.txt
                        '''
                    } else {
                        bat '''
                            if not exist .venv (
                                python -m venv .venv
                            )
                            call .venv\\Scripts\\activate
                            python -m pip install --upgrade pip
                            pip install -r requirements.txt
                        '''
                    }
                }
            }
        }

        stage('Verificar Conexión a Base de Datos (Supabase)') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            . .venv/bin/activate
                            python manage.py check --database default
                        '''
                    } else {
                        bat '''
                            call .venv\\Scripts\\activate
                            python manage.py check --database default
                        '''
                    }
                }
            }
        }

        stage('Sincronizar e Ingestar Cursos') {
            when {
                expression { params.SYNC_TARGET == 'courses' || params.SYNC_TARGET == 'all' }
            }
            steps {
                script {
                    def extraArgs = ""
                    if (params.DRY_RUN) {
                        extraArgs += " --dry-run"
                    }
                    if (params.LIMIT && params.LIMIT.trim() != "") {
                        extraArgs += " --limit " + params.LIMIT.trim()
                    }

                    def cmdArgs = ""
                    if (params.GROUP && params.GROUP != 'all_groups') {
                        cmdArgs = "--group " + params.GROUP + extraArgs
                    } else {
                        cmdArgs = "--source " + params.SOURCE + extraArgs
                    }

                    echo "============================================================"
                    echo "Ejecutando sync_courses con argumentos: ${cmdArgs}"
                    echo "============================================================"

                    if (isUnix()) {
                        sh """
                            . .venv/bin/activate
                            python manage.py sync_courses ${cmdArgs}
                        """
                    } else {
                        bat """
                            call .venv\\Scripts\\activate
                            python manage.py sync_courses ${cmdArgs}
                        """
                    }
                }
            }
        }

        stage('Sincronizar e Ingestar Vacantes de Empleo') {
            when {
                expression { params.SYNC_TARGET == 'jobs' || params.SYNC_TARGET == 'all' }
            }
            steps {
                script {
                    def extraArgs = ""
                    if (params.DRY_RUN) {
                        extraArgs += " --dry-run"
                    }
                    if (params.LIMIT && params.LIMIT.trim() != "") {
                        extraArgs += " --limit " + params.LIMIT.trim()
                    }

                    def jobCmdArgs = ""
                    if (params.JOB_GROUP && params.JOB_GROUP != 'all_groups') {
                        jobCmdArgs = "--group " + params.JOB_GROUP + extraArgs
                    } else {
                        jobCmdArgs = "--source " + params.JOB_SOURCE + extraArgs
                    }

                    echo "============================================================"
                    echo "Ejecutando sync_jobs con argumentos: ${jobCmdArgs}"
                    echo "============================================================"

                    if (isUnix()) {
                        sh """
                            . .venv/bin/activate
                            python manage.py sync_jobs ${jobCmdArgs}
                        """
                    } else {
                        bat """
                            call .venv\\Scripts\\activate
                            python manage.py sync_jobs ${jobCmdArgs}
                        """
                    }
                }
            }
        }
    }

    post {
        success {
            echo "============================================================"
            echo "¡Sincronización completada exitosamente! Base de datos Supabase actualizada."
            echo "============================================================"
        }
        failure {
            echo "============================================================"
            echo "ALERTA: Ocurrió un error en el pipeline de sincronización."
            echo "============================================================"
        }
    }
}
