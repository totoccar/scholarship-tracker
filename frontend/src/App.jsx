import React, { useEffect, useMemo, useState } from 'react';

const API_BASE_URL = (
    import.meta.env.VITE_API_BASE_URL ||
    `${window.location.protocol}//${window.location.hostname}:8080/api/v1/scholarships`
).replace(/\/$/, '');
const PAGE_SIZE = 6;

function truncate(text, max = 140) {
    if (!text) return '';
    return text.length > max ? `${text.slice(0, max)}...` : text;
}

async function fetchWithRetry(url, attempts = 3, delayMs = 450) {
    let lastError;
    for (let i = 0; i < attempts; i += 1) {
        try {
            return await fetch(url);
        } catch (error) {
            lastError = error;
            if (i < attempts - 1) {
                await new Promise((resolve) => setTimeout(resolve, delayMs));
            }
        }
    }
    throw lastError;
}

export default function App() {
    const [allItems, setAllItems] = useState([]);
    const [country, setCountry] = useState('');
    const [keyword, setKeyword] = useState('');
    const [page, setPage] = useState(0);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const countryOptions = useMemo(() => {
        const countries = allItems
            .map((item) => (item.country || 'Global').trim())
            .filter(Boolean);
        return [...new Set(countries)].sort((a, b) => a.localeCompare(b, 'es'));
    }, [allItems]);

    const filteredItems = useMemo(() => {
        const normalizedKeyword = keyword.trim().toLowerCase();

        return allItems.filter((item) => {
            const itemCountry = item.country || 'Global';
            const matchesCountry = country ? itemCountry.toLowerCase() === country.toLowerCase() : true;
            if (!matchesCountry) return false;

            if (!normalizedKeyword) return true;

            const haystack = [
                item.title,
                item.description,
                item.provider,
                item.country,
                ...(item.tags || []),
            ]
                .filter(Boolean)
                .join(' ')
                .toLowerCase();

            return haystack.includes(normalizedKeyword);
        });
    }, [allItems, country, keyword]);

    const totalElements = filteredItems.length;
    const totalPages = Math.max(1, Math.ceil(totalElements / PAGE_SIZE));

    const pagedItems = useMemo(() => {
        const start = page * PAGE_SIZE;
        return filteredItems.slice(start, start + PAGE_SIZE);
    }, [filteredItems, page]);

    const pageIndicator = useMemo(() => {
        const uiPage = page + 1;
        return `Pagina ${uiPage} de ${totalPages}`;
    }, [page, totalPages]);

    async function loadScholarships() {
        setLoading(true);
        setError('');

        try {
            const response = await fetchWithRetry(API_BASE_URL);
            if (!response.ok) {
                throw new Error(`Error HTTP ${response.status}`);
            }

            const data = await response.json();
            setAllItems(Array.isArray(data) ? data : []);
        } catch (err) {
            setAllItems([]);
            setError(`No se pudieron cargar becas: ${err.message}`);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        loadScholarships();
    }, []);

    useEffect(() => {
        setPage(0);
    }, [country, keyword]);

    const onResetFilters = () => {
        setCountry('');
        setKeyword('');
        setPage(0);
    };

    const onPrev = () => {
        if (page <= 0) return;
        setPage((current) => current - 1);
    };

    const onNext = () => {
        if (page >= totalPages - 1) return;
        setPage((current) => current + 1);
    };

    const showEmptyState = !loading && !error && pagedItems.length === 0;

    return (
        <div className="wrapper">
            <section className="hero">
                <p className="kicker">Scholarship Tracker</p>
                <h1>Buscador de Becas por Filtros</h1>
                <p className="subtitle">
                    Busca por palabra clave y filtra por pais con opciones reales detectadas del dataset.
                </p>

                <div className="search-panel filters-panel">
                    <input
                        type="text"
                        placeholder="Palabra clave: data, ingenieria, policy..."
                        autoComplete="off"
                        value={keyword}
                        onChange={(e) => setKeyword(e.target.value)}
                    />
                    <select value={country} onChange={(e) => setCountry(e.target.value)}>
                        <option value="">Todos los paises</option>
                        {countryOptions.map((countryOption) => (
                            <option key={countryOption} value={countryOption}>
                                {countryOption}
                            </option>
                        ))}
                    </select>
                    <button type="button" onClick={onResetFilters}>
                        Limpiar filtros
                    </button>
                </div>

                <div className="toolbar">
                    <span>{loading ? 'Buscando becas...' : `${totalElements} resultado(s) encontrados`}</span>
                    <span>{`Filtro pais: ${country || 'Todos'} | Keyword: ${keyword.trim() || 'Ninguna'}`}</span>
                </div>
            </section>

            {error && <section className="status error">{error}</section>}
            {showEmptyState && <section className="status">No encontramos becas para estos filtros. Prueba otra combinacion.</section>}

            <section className="grid">
                {pagedItems.map((scholarship) => (
                    <article className="card" key={scholarship.id ?? scholarship.url}>
                        <p className="provider">{scholarship.provider || 'Proveedor'}</p>
                        <h3 className="title">{scholarship.title || 'Sin titulo'}</h3>
                        <p className="meta">Pais: {scholarship.country || 'Global'} | Cierre: {scholarship.deadline || 'N/D'}</p>
                        <p className="description">{truncate(scholarship.description, 160)}</p>
                        <div className="tags">
                            {(scholarship.tags || []).map((tag) => (
                                <span className="tag" key={`${scholarship.url}-${tag}`}>
                                    {tag}
                                </span>
                            ))}
                        </div>
                        <div className="cta">
                            <a href={scholarship.url} target="_blank" rel="noopener noreferrer">
                                Ver convocatoria
                            </a>
                        </div>
                    </article>
                ))}
            </section>

            <div className="pager">
                <button type="button" onClick={onPrev} disabled={page <= 0}>
                    Anterior
                </button>
                <span>{pageIndicator}</span>
                <button type="button" onClick={onNext} disabled={page >= totalPages - 1 || totalElements === 0}>
                    Siguiente
                </button>
            </div>
        </div>
    );
}
