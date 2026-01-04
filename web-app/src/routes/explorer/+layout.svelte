<script lang="ts">
	import type { LayoutData } from './$types';
	
	let { data, children } = $props<{ data: LayoutData; children: any }>();
</script>

{@render children()}

