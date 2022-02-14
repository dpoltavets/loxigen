
    @Override
    public <F extends OFValueType<F>> F get(MatchField<F> field)
            throws UnsupportedOperationException {
        // FIXME yotam - please replace with real implementation
        return null;
    }

    @Override
    public <F extends OFValueType<F>> Masked<F> getMasked(MatchField<F> field)
            throws UnsupportedOperationException {
        // FIXME yotam - please replace with real implementation
        return null;
    }

    @Override
    public boolean supports(MatchField<?> field) {
        // FIXME yotam - please replace with real implementation
        return false;
    }

    @Override
    public boolean supportsMasked(MatchField<?> field) {
        // FIXME yotam - please replace with real implementation
        return false;
    }

    @Override
    public boolean isExact(MatchField<?> field) {
        // FIXME yotam - please replace with real implementation
        return false;
    }

    @Override
    public boolean isFullyWildcarded(MatchField<?> field) {
        // FIXME yotam - please replace with real implementation
        return false;
    }

    @Override
    public boolean isPartiallyMasked(MatchField<?> field) {
        // FIXME yotam - please replace with real implementation
        return false;
    }

    @Override
    public Iterable<MatchField<?>> getMatchFields() {
        throw new UnsupportedOperationException();
    }

    @Override
    public <F extends OFValueType<F>> F getWithoutPrerequisitesCheck(MatchField<F> field)
            throws UnsupportedOperationException {
            throw new UnsupportedOperationException();
            }

    @Override
    public <F extends OFValueType<F>> Masked<F> getMaskedWithoutPrerequisitesCheck(MatchField<F> field)
            throws UnsupportedOperationException {
            throw new UnsupportedOperationException();
            }

    @Override
    public Iterable<MatchField<?>> getMatchFieldsWithoutPrerequisitesCheck() {
            throw new UnsupportedOperationException();
            }

    @Override
    public boolean isExactWithoutPrerequisitesCheck(MatchField<?> field) throws UnsupportedOperationException {
            throw new UnsupportedOperationException();
            }
