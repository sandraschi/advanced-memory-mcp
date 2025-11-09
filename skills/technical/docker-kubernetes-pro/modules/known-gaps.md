# Known Gaps & Validation Tasks

## Open Items
- ⏳ Evaluate WASM-based workloads (Spin, wasmCloud) and capture best practices for mixed clusters.  
- ⏳ Document container-native storage (Portworx, OpenEBS) trade-offs vs managed storage.  
- ⏳ Compare multi-tenant isolation models (virtual clusters, vClusters, namespaces) for enterprise rollout.

## TODOs
1. Build reference GitOps repo showcasing blue/green + canary with Argo Rollouts.  
2. Pilot Sigstore policy enforcement with Kyverno in staging; document rollout steps.  
3. Create cost optimization playbook integrating Kubecost reports with finance review.

## Notes
- Raise confidence to **high** once WASM guidance and Sigstore enforcement patterns are validated.  
- Keep watch on Kubernetes deprecations (PodSecurityPolicy removal successors, API removals) each release.*** End Patch
