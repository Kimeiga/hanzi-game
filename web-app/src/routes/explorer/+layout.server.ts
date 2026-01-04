// Server-side layout loader for explorer pages
// This loads the semantic graph ONCE and makes it available to all child pages

import { getSemanticGraph, getCharGlosses, buildCharToBreadcrumb } from '$lib/server/data';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async () => {
	const semanticGraph = await getSemanticGraph();
	const charGlosses = await getCharGlosses();
	const charToBreadcrumb = buildCharToBreadcrumb(semanticGraph);

	return {
		semanticGraph,
		charGlosses,
		charToBreadcrumb
	};
};

