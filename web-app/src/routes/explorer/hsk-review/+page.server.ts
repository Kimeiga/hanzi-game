// Server-side loader for HSK review page
import { getHskWords } from '$lib/server/data';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
	return {
		hskData: getHskWords()
	};
};

