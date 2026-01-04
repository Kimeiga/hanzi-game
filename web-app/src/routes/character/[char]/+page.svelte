<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';

	interface ComponentData {
		char: string;
		gloss: string;
	}

	interface EquationData {
		char: string;
		gloss: string;
		components: ComponentData[];
		equation: string;
	}

	interface CharInfo {
		char: string;
		keyword: string;
		pinyin: string;
		meaning: string;
		simp: string | null;
	}

	let loading = $state(true);
	let error = $state<string | null>(null);
	let charParam = $state('');
	let equation = $state<EquationData | null>(null);
	let charInfo = $state<CharInfo | null>(null);

	// Data stores
	let equations = $state<Record<string, EquationData>>({});
	let glosses = $state<Record<string, string>>({});
	let graph = $state<any>(null);

	onMount(async () => {
		charParam = decodeURIComponent($page.params.char);
		
		try {
			// Load data
			const [eqRes, glossRes, graphRes] = await Promise.all([
				fetch('/game_data/character_equations.json'),
				fetch('/game_data/component_glosses.json'),
				fetch('/game_data/hanzi_semantic_graph.json')
			]);
			
			equations = await eqRes.json();
			glosses = await glossRes.json();
			graph = await graphRes.json();
			
			// Get equation data
			equation = equations[charParam] || null;
			
			// Find character info in graph
			charInfo = findCharInGraph(charParam, graph);
			
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load data';
		}
		
		loading = false;
	});

	function findCharInGraph(char: string, node: any): CharInfo | null {
		if (node.char === char) {
			return {
				char: node.char,
				keyword: node.keyword || '',
				pinyin: node.pinyin || '',
				meaning: node.meaning || '',
				simp: node.simp
			};
		}
		if (node.children) {
			for (const child of node.children) {
				const found = findCharInGraph(char, child);
				if (found) return found;
			}
		}
		return null;
	}

	function getGlyphWikiUrl(char: string): string {
		if (char.startsWith('&') && char.endsWith(';')) {
			const entity = char.slice(1, -1);
			if (entity.startsWith('CDP-')) {
				const hex = entity.substring(4).toLowerCase();
				return `https://glyphwiki.org/glyph/cdp-${hex}.svg`;
			}
			return `https://glyphwiki.org/glyph/${entity.toLowerCase()}.svg`;
		}
		const codePoint = char.codePointAt(0);
		if (!codePoint) return '';
		const hex = codePoint.toString(16).padStart(4, '0');
		return `https://glyphwiki.org/glyph/u${hex}.svg`;
	}
</script>

<svelte:head>
	<title>{charParam} - Character Details</title>
</svelte:head>

<div class="container">
	{#if loading}
		<div class="loading">Loading...</div>
	{:else if error}
		<div class="error">{error}</div>
	{:else}
		<header class="char-header">
			<div class="main-char">
				<img src={getGlyphWikiUrl(charParam)} alt={charParam} class="char-glyph" 
					onerror={(e) => { e.currentTarget.style.display = 'none'; }} />
				<span class="char-fallback">{charParam}</span>
			</div>
			{#if charInfo}
				<h1 class="keyword">{charInfo.keyword}</h1>
				{#if charInfo.pinyin}
					<p class="pinyin">{charInfo.pinyin}</p>
				{/if}
			{:else if glosses[charParam]}
				<h1 class="keyword">{glosses[charParam]}</h1>
			{:else}
				<h1 class="keyword">{charParam}</h1>
			{/if}
		</header>

		{#if equation}
			<section class="equation-section">
				<h2>Character Equation</h2>
				<div class="equation-display">
					<span class="result-char">{equation.char}</span>
					<span class="equals">=</span>
					{#each equation.components as comp, i (comp.char + i)}
						{#if i > 0}
							<span class="plus">+</span>
						{/if}
						<a href="/character/{encodeURIComponent(comp.char)}" class="component">
							<img src={getGlyphWikiUrl(comp.char)} alt={comp.char} class="comp-glyph"
								onerror={(e) => { e.currentTarget.style.display = 'none'; }} />
							<span class="comp-fallback">{comp.char}</span>
							{#if comp.gloss}
								<span class="comp-gloss">({comp.gloss})</span>
							{/if}
						</a>
					{/each}
				</div>
				<p class="equation-text">{equation.equation}</p>
			</section>
		{:else}
			<section class="equation-section">
				<h2>Character Equation</h2>
				<p class="no-equation">No decomposition available for this character.</p>
			</section>
		{/if}

		{#if charInfo?.meaning}
			<section class="meaning-section">
				<h2>Meaning</h2>
				<p>{charInfo.meaning}</p>
			</section>
		{/if}

		<a href="/explorer" class="back-link">← Back to Explorer</a>
	{/if}
</div>

<style>
	.container {
		max-width: 800px;
		margin: 0 auto;
		padding: 2rem;
	}

	.loading, .error {
		text-align: center;
		padding: 2rem;
		font-size: 1.2rem;
	}

	.error {
		color: #dc2626;
	}

	.char-header {
		text-align: center;
		margin-bottom: 2rem;
	}

	.main-char {
		position: relative;
		display: inline-block;
	}

	.char-glyph {
		width: 120px;
		height: 120px;
	}

	.char-fallback {
		font-size: 6rem;
		line-height: 1;
	}

	.keyword {
		font-size: 2rem;
		margin: 0.5rem 0;
		color: #1e293b;
	}

	.pinyin {
		font-size: 1.2rem;
		color: #64748b;
		margin: 0;
	}

	.equation-section, .meaning-section {
		background: #f8fafc;
		border-radius: 12px;
		padding: 1.5rem;
		margin-bottom: 1.5rem;
	}

	h2 {
		font-size: 1.2rem;
		color: #475569;
		margin: 0 0 1rem 0;
		border-bottom: 1px solid #e2e8f0;
		padding-bottom: 0.5rem;
	}

	.equation-display {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		justify-content: center;
		gap: 0.75rem;
		font-size: 1.5rem;
		margin-bottom: 1rem;
	}

	.result-char {
		font-size: 3rem;
	}

	.equals, .plus {
		color: #64748b;
		font-weight: 300;
	}

	.component {
		display: flex;
		flex-direction: column;
		align-items: center;
		text-decoration: none;
		color: inherit;
		padding: 0.5rem;
		border-radius: 8px;
		transition: background 0.2s;
	}

	.component:hover {
		background: #e2e8f0;
	}

	.comp-glyph {
		width: 48px;
		height: 48px;
	}

	.comp-fallback {
		font-size: 2rem;
	}

	.comp-gloss {
		font-size: 0.875rem;
		color: #64748b;
	}

	.equation-text {
		text-align: center;
		font-family: monospace;
		color: #475569;
		font-size: 1rem;
		margin: 0;
	}

	.no-equation {
		text-align: center;
		color: #94a3b8;
		font-style: italic;
	}

	.meaning-section p {
		margin: 0;
		line-height: 1.6;
	}

	.back-link {
		display: inline-block;
		color: #3b82f6;
		text-decoration: none;
		margin-top: 1rem;
	}

	.back-link:hover {
		text-decoration: underline;
	}
</style>

