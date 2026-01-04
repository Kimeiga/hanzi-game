// Server-side loader for JLPT review page
import { getJlptKanji, getKanjiDetails, type DataLoadContext } from '$lib/server/data';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, url }) => {
	const ctx: DataLoadContext = { fetch, origin: url.origin };
	return {
		jlptData: await getJlptKanji(ctx),
		kanjiDetails: await getKanjiDetails(ctx)
	};
};

