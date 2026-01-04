<script lang="ts">
	import type { PageData } from './$types';

	interface CharacterInfo {
		char: string;
		keyword: string;
		breadcrumb: string;
		jlpt: string;
		meaning: string;
		frequency: number;
	}

	// Server-loaded data
	let { data } = $props<{ data: PageData }>();

	let searchQuery = $state('');
	let sortBy = $state<'frequency' | 'jlpt' | 'char'>('frequency');
	let filterJlpt = $state('all');

	const jlptLevels = ['all', 'N5', 'N4', 'N3', 'N2', 'N1'];

	// Find keyword in semantic graph
	function findKeyword(char: string, node: any): string | null {
		if (node.char === char && node.keyword) return node.keyword;
		if (node.children) {
			for (const child of node.children) {
				const found = findKeyword(char, child);
				if (found) return found;
			}
		}
		return null;
	}

	// Compute all characters from Joyo list
	let characters: CharacterInfo[] = $derived.by(() => {
		return data.joyoList.map((char: string) => {
			let keyword = data.charGlosses[char] || '?';
			const graphKeyword = findKeyword(char, data.semanticGraph);
			if (graphKeyword) keyword = graphKeyword;

			const breadcrumb = data.charToBreadcrumb[char] || 'Not in semantic graph';
			const details = data.kanjiDetails[char] || {};
			const meaning = details.meaning || '';
			const jlpt = data.charToJlpt[char] || details.jlpt || 'Unknown';
			const frequency = details.frequency || 9999;

			return { char, keyword, breadcrumb, jlpt, meaning, frequency };
		});
	});

	let filteredCharacters: CharacterInfo[] = $derived.by(() => {
		let result = characters;

		// Filter by JLPT level
		if (filterJlpt !== 'all') {
			result = result.filter(c => c.jlpt === filterJlpt);
		}

		// Filter by search
		if (searchQuery) {
			result = result.filter(c =>
				c.char.includes(searchQuery) ||
				c.keyword.toLowerCase().includes(searchQuery.toLowerCase()) ||
				c.breadcrumb.toLowerCase().includes(searchQuery.toLowerCase()) ||
				c.meaning.toLowerCase().includes(searchQuery.toLowerCase())
			);
		}

		// Sort
		if (sortBy === 'frequency') {
			result = [...result].sort((a, b) => a.frequency - b.frequency);
		} else if (sortBy === 'jlpt') {
			const order = { 'N5': 0, 'N4': 1, 'N3': 2, 'N2': 3, 'N1': 4, 'Unknown': 5 };
			result = [...result].sort((a, b) =>
				(order[a.jlpt as keyof typeof order] ?? 5) - (order[b.jlpt as keyof typeof order] ?? 5)
			);
		}

		return result;
	});
</script>

<svelte:head>
	<title>常用漢字 Jōyō Kanji Review</title>
</svelte:head>

<div class="container">
	<header>
		<h1>🇯🇵 常用漢字 Jōyō Kanji</h1>
		<p class="subtitle">All 2,136 kanji designated by Japan's Ministry of Education for everyday use</p>
		<a href="/explorer" class="back-link">← Back to Explorer</a>
	</header>

	<div class="controls">
		<div class="filter-group">
			<label for="jlpt-filter">JLPT Level:</label>
			<select id="jlpt-filter" bind:value={filterJlpt}>
				{#each jlptLevels as level}
					<option value={level}>{level === 'all' ? 'All Levels' : level}</option>
				{/each}
			</select>
		</div>

		<div class="filter-group">
			<label for="sort-select">Sort by:</label>
			<select id="sort-select" bind:value={sortBy}>
				<option value="frequency">Frequency</option>
				<option value="jlpt">JLPT Level</option>
				<option value="char">Character</option>
			</select>
		</div>
		
		<input
			type="text"
			placeholder="Search kanji, keywords, or categories..."
			bind:value={searchQuery}
			class="search-input"
		/>
	</div>

	<div class="stats">
		Showing {filteredCharacters.length} of {characters.length} kanji
		{#if filterJlpt !== 'all'}(JLPT {filterJlpt}){/if}
	</div>

	<div class="character-grid">
		{#each filteredCharacters as { char, keyword, breadcrumb, jlpt, meaning } (char)}
			<a href="/character/{encodeURIComponent(char)}" class="char-card" class:uncategorized={breadcrumb === 'Not in semantic graph'}>
				<div class="jlpt-badge">{jlpt}</div>
				<div class="char">{char}</div>
				<div class="keyword">{keyword}</div>
				{#if meaning && meaning !== keyword}
					<div class="meaning">{meaning}</div>
				{/if}
				<div class="breadcrumb">{breadcrumb}</div>
			</a>
		{/each}
	</div>
</div>

<style>
	.container {
		max-width: 1400px;
		margin: 0 auto;
		padding: 2rem;
		font-family: system-ui, -apple-system, sans-serif;
	}

	header { margin-bottom: 2rem; }
	h1 { font-size: 2rem; margin-bottom: 0.5rem; }
	.subtitle { color: #666; margin-bottom: 1rem; }

	.back-link { color: #4a90d9; text-decoration: none; }
	.back-link:hover { text-decoration: underline; }

	.controls {
		display: flex;
		flex-wrap: wrap;
		gap: 1rem;
		margin-bottom: 1.5rem;
		align-items: center;
	}

	.filter-group {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.filter-group label { font-size: 0.9rem; color: #666; }

	.filter-group select {
		padding: 0.5rem;
		border: 1px solid #ddd;
		border-radius: 4px;
		font-size: 0.9rem;
	}

	.search-input {
		flex: 1;
		min-width: 200px;
		padding: 0.5rem 1rem;
		border: 1px solid #ddd;
		border-radius: 4px;
		font-size: 1rem;
	}

	.stats { color: #666; margin-bottom: 1rem; font-size: 0.9rem; }
	.loading { text-align: center; padding: 3rem; color: #666; }

	.character-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
		gap: 1rem;
	}

	.char-card {
		display: block;
		text-decoration: none;
		color: inherit;
		border: 1px solid #e0e0e0;
		border-radius: 8px;
		padding: 1rem;
		background: white;
		transition: box-shadow 0.2s, transform 0.2s;
		position: relative;
	}
	.char-card:hover {
		box-shadow: 0 2px 8px rgba(0,0,0,0.1);
		transform: translateY(-2px);
	}
	.char-card.uncategorized { border-color: #ffcc80; background: #fff8e1; }

	.jlpt-badge {
		position: absolute;
		top: 0.5rem;
		right: 0.5rem;
		font-size: 0.7rem;
		padding: 0.15rem 0.4rem;
		border-radius: 3px;
		background: #e53935;
		color: white;
		font-weight: 600;
	}

	.char { font-size: 2.5rem; text-align: center; margin-bottom: 0.5rem; }
	.keyword { font-weight: 600; text-align: center; margin-bottom: 0.25rem; color: #333; }
	.meaning { font-size: 0.85rem; text-align: center; color: #666; margin-bottom: 0.5rem; }
	.breadcrumb { font-size: 0.75rem; color: #888; text-align: center; line-height: 1.4; }
</style>

