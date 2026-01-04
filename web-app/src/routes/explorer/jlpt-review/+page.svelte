<script lang="ts">
	import type { PageData } from './$types';

	// Server-loaded data
	let { data } = $props<{ data: PageData }>();

	let selectedLevel = $state('N5');
	let searchQuery = $state('');

	const levelOrder = ['N5', 'N4', 'N3', 'N2', 'N1'];

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

	// Compute characters for selected level
	let characters = $derived.by(() => {
		const jlptLevel = data.jlptData[selectedLevel];
		if (!jlptLevel) return [];

		const uniqueChars = [...new Set(jlptLevel)] as string[];

		return uniqueChars.map((char: string) => {
			let keyword = data.charGlosses[char] || '?';
			const graphKeyword = findKeyword(char, data.semanticGraph);
			if (graphKeyword) keyword = graphKeyword;

			const breadcrumb = data.charToBreadcrumb[char] || 'Not in semantic graph';
			const meaning = data.kanjiDetails[char]?.meaning || '';

			return { char, keyword, breadcrumb, level: selectedLevel, meaning };
		});
	});

	let filteredCharacters = $derived(
		searchQuery
			? characters.filter(c =>
				c.char.includes(searchQuery) ||
				c.keyword.toLowerCase().includes(searchQuery.toLowerCase()) ||
				c.breadcrumb.toLowerCase().includes(searchQuery.toLowerCase()) ||
				c.meaning.toLowerCase().includes(searchQuery.toLowerCase())
			)
			: characters
	);
</script>

<svelte:head>
	<title>JLPT Kanji Review</title>
</svelte:head>

<div class="container">
	<header>
		<h1>🇯🇵 JLPT Kanji Review</h1>
		<p class="subtitle">Review glosses and semantic categorization for JLPT kanji (Japanese Language Proficiency Test)</p>
		<a href="/explorer" class="back-link">← Back to Explorer</a>
	</header>

	<div class="controls">
		<div class="level-selector">
			{#each levelOrder as level}
				{#if data.jlptData[level]}
					<button
						class="level-btn"
						class:active={selectedLevel === level}
						onclick={() => selectedLevel = level}
					>
						{level} ({data.jlptData[level]?.length || 0})
					</button>
				{/if}
			{/each}
		</div>

		<input
			type="text"
			placeholder="Search kanji, keywords, or categories..."
			bind:value={searchQuery}
			class="search-input"
		/>
	</div>

	<div class="stats">
		Showing {filteredCharacters.length} of {characters.length} kanji in {selectedLevel}
	</div>

	<div class="character-grid">
		{#each filteredCharacters as { char, keyword, breadcrumb, meaning } (char)}
			<a href="/character/{encodeURIComponent(char)}" class="char-card" class:uncategorized={breadcrumb === 'Not in semantic graph'}>
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

	.back-link {
		color: #4a90d9;
		text-decoration: none;
	}
	.back-link:hover { text-decoration: underline; }

	.controls {
		display: flex;
		flex-wrap: wrap;
		gap: 1rem;
		margin-bottom: 1.5rem;
		align-items: center;
	}

	.level-selector {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
	}

	.level-btn {
		padding: 0.5rem 1rem;
		border: 1px solid #ddd;
		background: white;
		border-radius: 4px;
		cursor: pointer;
		font-size: 0.9rem;
	}
	.level-btn:hover { background: #f5f5f5; }
	.level-btn.active {
		background: #e53935;
		color: white;
		border-color: #e53935;
	}

	.search-input {
		flex: 1;
		min-width: 200px;
		padding: 0.5rem 1rem;
		border: 1px solid #ddd;
		border-radius: 4px;
		font-size: 1rem;
	}

	.stats {
		color: #666;
		margin-bottom: 1rem;
		font-size: 0.9rem;
	}

	.loading {
		text-align: center;
		padding: 3rem;
		color: #666;
	}

	.character-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
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
	}
	.char-card:hover {
		box-shadow: 0 2px 8px rgba(0,0,0,0.1);
		transform: translateY(-2px);
	}
	.char-card.uncategorized {
		border-color: #ffcc80;
		background: #fff8e1;
	}

	.char {
		font-size: 2.5rem;
		text-align: center;
		margin-bottom: 0.5rem;
	}

	.keyword {
		font-weight: 600;
		text-align: center;
		margin-bottom: 0.25rem;
		color: #333;
	}

	.meaning {
		font-size: 0.85rem;
		text-align: center;
		color: #666;
		margin-bottom: 0.5rem;
	}

	.breadcrumb {
		font-size: 0.75rem;
		color: #888;
		text-align: center;
		line-height: 1.4;
	}
</style>

