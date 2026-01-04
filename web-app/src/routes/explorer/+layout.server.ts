// Server-side layout loader for explorer pages
// This loads the semantic graph ONCE and makes it available to all child pages

import { getSemanticGraph, getCharGlosses, buildCharToBreadcrumb, type DataLoadContext } from '$lib/server/data';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ fetch, url }) => {
	const ctx: DataLoadContext = { fetch, origin: url.origin };

	const semanticGraph = await getSemanticGraph(ctx);
	const charGlosses = await getCharGlosses(ctx);
	const charToBreadcrumb = buildCharToBreadcrumb(semanticGraph);

	return {
		semanticGraph,
		charGlosses,
		charToBreadcrumb
	};
};

