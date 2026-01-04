// Server-side loader for category page
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
	return {
		categoryName: params.category
	};
};

