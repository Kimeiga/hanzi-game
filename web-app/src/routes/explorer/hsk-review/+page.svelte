<script lang="ts">
	import type { PageData } from './$types';

	// Server-loaded data
	let { data } = $props<{ data: PageData }>();

	let selectedLevel = $state('1');
	let searchQuery = $state('');

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
		const hskLevel = data.hskData[selectedLevel];
		if (!hskLevel) return [];

		const uniqueChars = [...new Set(hskLevel)] as string[];

		return uniqueChars.map((char: string) => {
			let keyword = data.charGlosses[char] || '?';
			const graphKeyword = findKeyword(char, data.semanticGraph);
			if (graphKeyword) keyword = graphKeyword;

			const breadcrumb = data.charToBreadcrumb[char] || 'Uncategorized';

			return { char, keyword, breadcrumb, level: selectedLevel };
		});
	});

	let filteredCharacters = $derived(
		searchQuery
			? characters.filter(c =>
				c.char.includes(searchQuery) ||
				c.keyword.toLowerCase().includes(searchQuery.toLowerCase()) ||
				c.breadcrumb.toLowerCase().includes(searchQuery.toLowerCase())
			)
			: characters
	);
</script>

<svelte:head>
	<title>HSK Character Review</title>
</svelte:head>

<div class="container">
	<header>
		<h1>HSK Character Review</h1>
		<p class="subtitle">Review glosses and semantic categorization for HSK characters</p>
		<a href="/explorer" class="back-link">← Back to Explorer</a>
	</header>

	<div class="controls">
		<div class="level-selector">
			{#each Object.keys(data.hskData).sort((a, b) => parseInt(a) - parseInt(b)) as level}
				<button
					class="level-btn"
					class:active={selectedLevel === level}
					onclick={() => selectedLevel = level}
				>
					HSK {level}
				</button>
			{/each}
		</div>

		<input
			type="text"
			placeholder="Search characters, keywords, or categories..."
			bind:value={searchQuery}
			class="search-input"
		/>
	</div>

	<div class="stats">
		Showing {filteredCharacters.length} of {characters.length} characters in HSK {selectedLevel}
	</div>

	<div class="character-grid">
		{#each filteredCharacters as { char, keyword, breadcrumb } (char)}
			<a href="/character/{encodeURIComponent(char)}" class="char-card">
				<div class="char">{char}</div>
				<div class="keyword">{keyword}</div>
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
		background: #4a90d9;
		color: white;
		border-color: #4a90d9;
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

	.char {
		font-size: 2.5rem;
		text-align: center;
		margin-bottom: 0.5rem;
	}

	.keyword {
		font-weight: 600;
		text-align: center;
		margin-bottom: 0.5rem;
		color: #333;
	}

	.breadcrumb {
		font-size: 0.75rem;
		color: #888;
		text-align: center;
		line-height: 1.4;
	}
</style>

