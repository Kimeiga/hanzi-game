// Server-side loader for JLPT review page
import { getJlptKanji, getKanjiDetails } from '$lib/server/data';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
	return {
		jlptData: getJlptKanji(),
		kanjiDetails: getKanjiDetails()
	};
};

