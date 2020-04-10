See https://driplineorg.github.io/controls-guide/develop/guides/first-mesh.html for the tutorial.

To run 
1) Install rabbitmq. One possibility is to install through helm. See: https://hub.helm.sh/charts/bitnami/rabbitmq
2) Create Kubernetes secret that contains your rabbitmq credentials. Edit rabbitmq-authentications-secret.yaml to include your rabbitmq cluster url and your rabbitmq login credentials. For documentation about secrets, see: https://kubernetes.io/docs/concepts/configuration/secret/
3) install chart and kv-store runtime-configuration with helm. Run a command similar to  
   ::
      helm install kv-store chart/ -f example/k8s/kv-store-values.yaml
   For more information about helm, see: https://helm.sh/docs/


