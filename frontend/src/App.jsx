import React, { useEffect, useMemo, useState } from 'react';

function resolveApiBaseUrl(value) {
    const fallbackPath = '/api/v1/scholarships';
    const rawValue = (value || '').trim().replace(/\/$/, '');

    if (!rawValue) {
        return fallbackPath;
    }

    if (rawValue.includes(fallbackPath)) {
        return rawValue;
    }

    return `${rawValue}${fallbackPath}`;
}

const API_BASE_URL = resolveApiBaseUrl(import.meta.env.VITE_API_BASE_URL);
const PAGE_SIZE = 6;

const ACADEMIC_LEVELS = {
    all: 'Todos los niveles',
    postgraduate: 'Posgrados',
    masters: 'Masters',
};

function matchesAcademicLevel(item, academicLevel) {
    if (academicLevel === 'all') return true;

    const haystack = [
        item.title,
        item.description,
        ...(item.tags || []),
    ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase();

    const postgraduateKeywords = [
        'posgrado',
        'postgrado',
        'postgraduate',
        'graduate',
        'maestria',
        'master',
        'msc',
        'mba',
    ];

    const mastersKeywords = ['master', 'masters', 'maestria', 'msc', 'mba'];

    if (academicLevel === 'postgraduate') {
        return postgraduateKeywords.some((keyword) => haystack.includes(keyword));
    }

    if (academicLevel === 'masters') {
        return mastersKeywords.some((keyword) => haystack.includes(keyword));
    }

    return true;
}

function truncate(text, max = 140) {
    if (!text) return '';
    return text.length > max ? `${text.slice(0, max)}...` : text;
}

function extractHost(rawUrl) {
    const value = (rawUrl || '').trim();
    if (!value) return '';

    try {
        const normalized = /^https?:\/\//i.test(value) ? value : `https://${value.replace(/^\/\//, '')}`;
        const host = new URL(normalized).hostname.toLowerCase();
        return host.startsWith('www.') ? host.slice(4) : host;
    } catch {
        return '';
    }
}

function resolveLogoUrl(item) {
    const hostFromScholarship = extractHost(item?.url);
    const hostFromLogo = extractHost(item?.logoUrl);
    const host = hostFromScholarship || hostFromLogo;

    if (!host) return '';
    return `https://www.google.com/s2/favicons?sz=64&domain=${encodeURIComponent(host)}`;
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

async function buildHttpError(response) {
    const fallback = `Error HTTP ${response.status}`;

    try {
        const payload = await response.json();
        if (payload && typeof payload.message === 'string' && payload.message.trim()) {
            return new Error(`${fallback}: ${payload.message.trim()}`);
        }
    } catch {
        // Ignore JSON parsing errors and keep fallback message.
    }

    return new Error(fallback);
}

export default function App() {
    const [allItems, setAllItems] = useState([]);
    const [country, setCountry] = useState('');
    const [keyword, setKeyword] = useState('');
    const [academicLevel, setAcademicLevel] = useState('all');
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
            const status = (item.status || 'APPROVED').toUpperCase();
            if (status !== 'APPROVED' && status !== 'REVIEW') return false;

            const itemCountry = item.country || 'Global';
            const matchesCountry = country ? itemCountry.toLowerCase() === country.toLowerCase() : true;
            if (!matchesCountry) return false;

            if (!matchesAcademicLevel(item, academicLevel)) return false;

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
    }, [allItems, country, keyword, academicLevel]);

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
                throw await buildHttpError(response);
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
    }, [country, keyword, academicLevel]);

    const onResetFilters = () => {
        setCountry('');
        setKeyword('');
        setAcademicLevel('all');
        setPage(0);
    };

    const activeFilters = [
        keyword.trim()
            ? {
                key: 'keyword',
                label: `Keyword: ${keyword.trim()}`,
                clear: () => setKeyword(''),
            }
            : null,
        country
            ? {
                key: 'country',
                label: `Pais: ${country}`,
                clear: () => setCountry(''),
            }
            : null,
        academicLevel !== 'all'
            ? {
                key: 'academicLevel',
                label: `Nivel: ${ACADEMIC_LEVELS[academicLevel]}`,
                clear: () => setAcademicLevel('all'),
            }
            : null,
    ].filter(Boolean);

    const onPrev = () => {
        if (page <= 0) return;
        setPage((current) => current - 1);
    };

    const onLogoLoadError = (event) => {
        event.currentTarget.style.display = 'none';
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

                    <select value={academicLevel} onChange={(e) => setAcademicLevel(e.target.value)}>
                        <option value="all">Todos los niveles</option>
                        <option value="postgraduate">Posgrados</option>
                        <option value="masters">Masters</option>
                    </select>

                    <button type="button" onClick={onResetFilters}>
                        Limpiar filtros
                    </button>
                </div>

                {activeFilters.length > 0 && (
                    <div className="active-filters">
                        {activeFilters.map((filter) => (
                            <span className="filter-chip" key={filter.key}>
                                {filter.label}
                                <button type="button" aria-label={`Quitar ${filter.label}`} onClick={filter.clear}>
                                    ×
                                </button>
                            </span>
                        ))}
                    </div>
                )}

                <div className="toolbar">
                    <span>{loading ? 'Buscando becas...' : `${totalElements} resultado(s) encontrados`}</span>
                    <span>{`Pais: ${country || 'Todos'} | Keyword: ${keyword.trim() || 'Ninguna'} | Nivel: ${ACADEMIC_LEVELS[academicLevel]}`}</span>
                </div>
            </section>

            {error && <section className="status error">{error}</section>}
            {showEmptyState && <section className="status">No encontramos becas para estos filtros. Prueba otra combinacion.</section>}

            <section className="grid">
                {pagedItems.map((scholarship) => (
                    <article className="card" key={scholarship.id ?? scholarship.url}>
                        {resolveLogoUrl(scholarship) && (
                            <img
                                src={resolveLogoUrl(scholarship)}
                                alt={`Logo de ${scholarship.provider || 'proveedor'}`}
                                width="36"
                                height="36"
                                style={{ borderRadius: '8px', objectFit: 'contain', marginBottom: '8px' }}
                                loading="lazy"
                                onError={onLogoLoadError}
                            />
                        )}
                        <p className="provider">{scholarship.provider || 'Proveedor'}</p>
                        <h3 className="title">{scholarship.title || 'Sin titulo'}</h3>
                        <p className="meta">Pais: {scholarship.country || 'Global'} | Cierre: {scholarship.deadline || 'N/D'}</p>
                        {scholarship.benefits && <p className="meta">Beneficios: {truncate(scholarship.benefits, 80)}</p>}
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
