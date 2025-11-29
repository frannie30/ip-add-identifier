document.addEventListener('DOMContentLoaded', () => {
    const entriesList = document.getElementById('entriesList');
    const entryDetail = document.getElementById('entryDetail');
    const deleteBtn = document.getElementById('deleteBtn');
    const openBtn = document.getElementById('openBtn');

    let currentEntryId = null;

    async function loadEntries() {
        entriesList.innerHTML = 'Loading saved entries...';
        try {
            const r = await fetch('/api/saved_entries');
            if (!r.ok) {
                throw new Error('Failed to load entries');
            }
            const body = await r.json();
            const entries = body.entries || [];
            if (entries.length === 0) {
                entriesList.innerHTML = '<p>No saved snapshots yet. Use the main page to save your current snapshot.</p>';
                return;
            }

            const ul = document.createElement('ul');
            ul.style.listStyle = 'none';
            ul.style.padding = '0';
            for (const e of entries) {
                const li = document.createElement('li');
                li.style.padding = '8px 10px';
                li.style.borderBottom = '1px solid rgba(255,255,255,0.06)';
                li.style.cursor = 'pointer';
                li.innerHTML = `<strong>${escapeHtml(e.title || 'Snapshot #' + e.id)}</strong> <span style="color:#aaa; font-size:0.9rem">${new Date(e.created_at).toLocaleString()}</span>`;
                li.addEventListener('click', () => { selectEntry(e.id); });
                ul.appendChild(li);
            }
            entriesList.innerHTML = '';
            entriesList.appendChild(ul);
        } catch (err) {
            entriesList.innerHTML = '<p>Error loading entries.</p>';
            console.error(err);
        }
    }

    async function selectEntry(id) {
        try {
            const r = await fetch('/api/saved_entries/' + id);
            if (!r.ok) throw new Error('Failed to load entry');
            const body = await r.json();
            const e = body.entry;
            currentEntryId = e.id;
            // Populate the styled detail card fields instead of showing raw JSON
            populateEntryDetails(e.data);
            deleteBtn.style.display = 'inline-block';
            if (openBtn) openBtn.style.display = 'inline-block';
        } catch (err) {
            // reset the detail fields but keep the layout
            populateEntryDetails(null);
            console.error(err);
        }
    }

    deleteBtn.addEventListener('click', async () => {
        if (!currentEntryId) return;
        if (!confirm('Delete this snapshot permanently?')) return;
        try {
            const r = await fetch('/api/saved_entries/' + currentEntryId, { method: 'DELETE' });
            if (!r.ok) throw new Error('Delete failed');
            // Refresh list — reset displayed details but keep layout
            currentEntryId = null;
            populateEntryDetails(null);
            deleteBtn.style.display = 'none';
            if (openBtn) openBtn.style.display = 'none';
            await loadEntries();
        } catch (err) {
            alert('Failed to delete');
            console.error(err);
        }
    });

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function setText(id, value) {
        const el = document.getElementById(id);
        if (!el) return;
        el.textContent = (value === undefined || value === null || value === '') ? '-' : value;
    }

    function populateEntryDetails(data) {
        if (!data || typeof data !== 'object') {
            entryDetail.querySelectorAll('span').forEach(s => s.textContent = '-');
            return;
        }

        // Addresses
        setText('snapshot_ipv4', data.addresses && data.addresses.ipv4 ? data.addresses.ipv4 : '-');
        setText('snapshot_ipv6', data.addresses && data.addresses.ipv6 ? data.addresses.ipv6 : '-');

        // Geolocation
        setText('snapshot_city', data.geolocation && data.geolocation.city ? data.geolocation.city : '-');
        setText('snapshot_region', data.geolocation && data.geolocation.region ? data.geolocation.region : '-');
        setText('snapshot_country', data.geolocation && data.geolocation.country ? data.geolocation.country : '-');
        setText('snapshot_country_code', data.geolocation && data.geolocation.country_code ? data.geolocation.country_code : '-');
        setText('snapshot_postal', data.geolocation && data.geolocation.postal_code ? data.geolocation.postal_code : '-');
        setText('snapshot_timezone', data.geolocation && data.geolocation.timezone ? data.geolocation.timezone : '-');
        if (data.geolocation && (data.geolocation.latitude || data.geolocation.longitude)) {
            const lat = data.geolocation.latitude || '-';
            const lon = data.geolocation.longitude || '-';
            setText('snapshot_coords', `${lat}, ${lon}`);
        } else {
            setText('snapshot_coords', '-');
        }

        // Local
        setText('snapshot_hostname', data.local && data.local.hostname ? data.local.hostname : (data.additional && data.additional.hostname ? data.additional.hostname : '-'));
        if (data.local && Array.isArray(data.local.local_ips)) {
            setText('snapshot_local_ips', data.local.local_ips.join(', '));
        } else if (data.local && data.local.local_ips) {
            setText('snapshot_local_ips', data.local.local_ips);
        } else {
            setText('snapshot_local_ips', '-');
        }
        if (data.timestamp) {
            try {
                const dt = new Date(data.timestamp);
                setText('snapshot_timestamp', isNaN(dt) ? data.timestamp : dt.toLocaleString());
            } catch (e) {
                setText('snapshot_timestamp', data.timestamp);
            }
        } else {
            setText('snapshot_timestamp', '-');
        }

        // Network
        setText('snapshot_isp', data.network && data.network.isp ? data.network.isp : '-');
        setText('snapshot_asn', data.network && data.network.as_number ? data.network.as_number : (data.network && data.network.asn ? data.network.asn : '-'));
        setText('snapshot_asdesc', data.network && data.network.as_description ? data.network.as_description : (data.network && data.network.as ? data.network.as : '-'));

        // Additional
        setText('snapshot_add_hostname', data.additional && data.additional.hostname ? data.additional.hostname : '-');
    }

    

    loadEntries();
    if (openBtn) {
        openBtn.addEventListener('click', () => {
            if (!currentEntryId) return;
            window.location.href = '/?load_entry=' + encodeURIComponent(currentEntryId);
        });
    }
});
